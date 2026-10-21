#!/usr/bin/env python3
"""Manual cropper — full height retained, width cropped via click."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageTk
import tkinter as tk

DEFAULT_ASPECT = "16:10"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
PARENT_DIR = Path(__file__).resolve().parent
DEFAULT_SOURCE_DIR = PARENT_DIR / "source_images"
DEFAULT_OUTPUT_DIR = PARENT_DIR / "cropped"


def ask(label: str, default: str) -> str:
    value = input(f"{label} [{default}]: ").strip()
    return value or default


def parse_aspect(text: str) -> tuple[float, float]:
    parts = text.strip().replace("/", ":").split(":")
    if len(parts) != 2:
        raise ValueError("use W:H, for example 16:10")
    width, height = float(parts[0]), float(parts[1])
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be greater than 0")
    return width, height


def ask_aspect(default: str = DEFAULT_ASPECT) -> tuple[float, float, str]:
    while True:
        raw = ask("Aspect ratio (W:H)", default)
        try:
            width, height = parse_aspect(raw)
        except ValueError as err:
            print(f"Invalid aspect ratio ({err}).")
            continue
        return width, height, raw


def ask_dir(label: str, default: Path, must_exist: bool) -> Path:
    while True:
        raw = ask(label, str(default))
        path = Path(raw).expanduser()
        if not path.is_absolute():
            path = PARENT_DIR / path
        path = path.resolve()
        if must_exist and not path.is_dir():
            print(f"Folder not found: {path}")
            continue
        return path


def list_images(folder: Path, output_dir: Path) -> list[Path]:
    return sorted(
        p
        for p in folder.iterdir()
        if p.is_file()
        and p.suffix.lower() in IMAGE_EXTS
        and not (output_dir / p.name).exists()
    )


def crop_width_for_height(height: int, aspect_w: float, aspect_h: float) -> int:
    return round(height * aspect_w / aspect_h)


def compute_crop_left(click_x: float | None, img_w: int, crop_w: int) -> int:
    """Resolve horizontal crop origin from a click (or None for center)."""
    if crop_w >= img_w:
        return 0

    if click_x is None:
        return (img_w - crop_w) // 2

    x = click_x
    can_fit_left = x >= crop_w  # room for crop to the left of click
    can_fit_right = x + crop_w <= img_w  # room for crop to the right of click

    if not can_fit_left and can_fit_right:
        # Left side → click is the left border
        left = x
    elif not can_fit_right and can_fit_left:
        # Right side → click is the right border
        left = x - crop_w
    else:
        # Both possible, or neither → center on click
        left = x - crop_w / 2

    return int(max(0, min(round(left), img_w - crop_w)))


class CropApp:
    def __init__(
        self,
        images: list[Path],
        output_dir: Path,
        aspect_w: float,
        aspect_h: float,
        aspect_label: str,
    ) -> None:
        self.pending = list(images)
        self.history: list[Path] = []
        self.review: int | None = None
        self.total = len(images)
        self.output_dir = output_dir
        self.aspect_w = aspect_w
        self.aspect_h = aspect_h
        self.aspect_label = aspect_label
        self.crop_box: tuple[int, int, int, int] | None = None  # left, top, right, bottom
        self.pil_image: Image.Image | None = None
        self.display_scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.photo: ImageTk.PhotoImage | None = None

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.root = tk.Tk()
        self.root.title(f"{aspect_label} Crop Tool")
        self.root.configure(bg="#1a1a1a")
        self.root.minsize(800, 500)

        header = tk.Frame(self.root, bg="#1a1a1a")
        header.pack(side=tk.TOP, fill=tk.X)

        self.counter = tk.Label(
            header,
            text="",
            fg="#ff3b30",
            bg="#1a1a1a",
            font=("Helvetica", 18, "bold"),
            padx=14,
            pady=8,
        )
        self.counter.pack(side=tk.LEFT)

        self.status = tk.Label(
            header,
            text="",
            fg="#cccccc",
            bg="#1a1a1a",
            font=("Helvetica", 13),
            pady=8,
            anchor=tk.W,
        )
        self.status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.hint = tk.Label(
            self.root,
            text="Click to place crop  ·  Enter to confirm  ·  Esc to clear  ·  → skip  ·  ← recrop",
            fg="#888888",
            bg="#1a1a1a",
            font=("Helvetica", 11),
            pady=4,
        )
        self.hint.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(self.root, bg="#111111", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Configure>", self.on_resize)
        self.root.bind_all("<Return>", self.on_enter)
        self.root.bind_all("<KP_Enter>", self.on_enter)
        self.root.bind_all("<Escape>", self.on_escape)
        self.root.bind_all("<Right>", self.on_right)
        self.root.bind_all("<Left>", self.on_left)

        self.load_current()

    def current_path(self) -> Path | None:
        if self.review is not None:
            return self.history[self.review]
        if not self.pending:
            return None
        return self.pending[0]

    def counter_text(self) -> str:
        if self.review is not None:
            current = self.review + 1
        elif not self.pending:
            current = self.total
        else:
            current = len(self.history) + 1
        return f"{current}/{self.total}"

    def load_current(self) -> None:
        path = self.current_path()
        self.crop_box = None
        self.counter.config(text=self.counter_text())
        if path is None:
            self.status.config(text="Done — all images cropped.")
            self.root.title(f"{self.aspect_label} Crop Tool")
            self.canvas.delete("all")
            self.pil_image = None
            return

        self.pil_image = Image.open(path).convert("RGB")
        self.root.title(f"{self.aspect_label} Crop Tool — {path.name}")
        note = "recrop  ·  " if self.review is not None else ""
        self.status.config(
            text=f"{note}{path.name}  ·  {self.pil_image.width}×{self.pil_image.height}"
        )
        self.render()

    def render(self) -> None:
        self.canvas.delete("all")
        if self.pil_image is None:
            return

        cw = max(self.canvas.winfo_width(), 1)
        ch = max(self.canvas.winfo_height(), 1)
        iw, ih = self.pil_image.size

        scale = min(cw / iw, ch / ih)
        dw, dh = max(1, int(iw * scale)), max(1, int(ih * scale))
        self.display_scale = scale
        self.offset_x = (cw - dw) // 2
        self.offset_y = (ch - dh) // 2

        display = self.pil_image.resize((dw, dh), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(display)
        self.canvas.create_image(self.offset_x, self.offset_y, anchor=tk.NW, image=self.photo)

        if self.crop_box is not None:
            self.draw_crop_overlay()

    def draw_crop_overlay(self) -> None:
        assert self.crop_box is not None
        left, top, right, bottom = self.crop_box
        s = self.display_scale
        ox, oy = self.offset_x, self.offset_y

        x0 = ox + left * s
        y0 = oy + top * s
        x1 = ox + right * s
        y1 = oy + bottom * s

        # Dim outside the crop
        iw, ih = self.pil_image.size  # type: ignore[union-attr]
        full_x0, full_y0 = ox, oy
        full_x1, full_y1 = ox + iw * s, oy + ih * s

        dim = "#000000"
        self.canvas.create_rectangle(full_x0, full_y0, x0, full_y1, fill=dim, stipple="gray50", outline="")
        self.canvas.create_rectangle(x1, full_y0, full_x1, full_y1, fill=dim, stipple="gray50", outline="")

        self.canvas.create_rectangle(x0, y0, x1, y1, outline="#00e5a8", width=2)
        # Corner ticks
        for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
            self.canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill="#00e5a8", outline="")

    def canvas_to_image_x(self, canvas_x: float) -> float | None:
        if self.pil_image is None:
            return None
        ix = (canvas_x - self.offset_x) / self.display_scale
        if ix < 0 or ix > self.pil_image.width:
            return None
        return ix

    def set_crop_from_click(self, click_x: float | None) -> None:
        if self.pil_image is None:
            return
        iw, ih = self.pil_image.size
        crop_w = crop_width_for_height(ih, self.aspect_w, self.aspect_h)
        left = compute_crop_left(click_x, iw, crop_w)
        self.crop_box = (left, 0, left + min(crop_w, iw), ih)
        self.render()

    def on_click(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        if self.pil_image is None:
            return
        ix = self.canvas_to_image_x(event.x)
        if ix is None:
            return
        self.set_crop_from_click(ix)

    def on_enter(self, _event: tk.Event | None = None) -> None:  # type: ignore[type-arg]
        if self.pil_image is None:
            return
        if self.crop_box is None:
            self.set_crop_from_click(None)
            return
        self.save_and_next()

    def on_escape(self, _event: tk.Event | None = None) -> None:  # type: ignore[type-arg]
        if self.crop_box is None:
            return
        self.crop_box = None
        self.render()

    def on_right(self, _event: tk.Event | None = None) -> None:  # type: ignore[type-arg]
        if self.review is not None:
            if self.review + 1 < len(self.history):
                self.review += 1
            else:
                self.review = None
            self.load_current()
            return
        if len(self.pending) < 2:
            return
        skipped = self.pending.pop(0)
        self.pending.append(skipped)
        print(f"Skipped {skipped.name}")
        self.load_current()

    def on_left(self, _event: tk.Event | None = None) -> None:  # type: ignore[type-arg]
        if not self.history:
            return
        if self.review is None:
            self.review = len(self.history) - 1
        elif self.review > 0:
            self.review -= 1
        else:
            return
        self.load_current()

    def on_resize(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        self.render()

    def save_and_next(self) -> None:
        if self.pil_image is None or self.crop_box is None:
            return
        path = self.current_path()
        if path is None:
            return
        cropped = self.pil_image.crop(self.crop_box)
        out = self.output_dir / path.name
        cropped.save(out, quality=95)
        print(f"Saved {out}  ({cropped.width}×{cropped.height})")
        if self.review is None:
            self.history.append(self.pending.pop(0))
        elif self.review + 1 < len(self.history):
            self.review += 1
        else:
            self.review = None
        self.load_current()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    aspect_w, aspect_h, aspect_label = ask_aspect()
    source_dir = ask_dir("Source folder", DEFAULT_SOURCE_DIR, must_exist=True)
    output_dir = ask_dir("Output folder", DEFAULT_OUTPUT_DIR, must_exist=False)

    images = list_images(source_dir, output_dir)
    if not images:
        print(f"No uncropped images left in {source_dir}")
        sys.exit(0)
    print(f"{len(images)} remaining at {aspect_label} → {output_dir}")
    CropApp(images, output_dir, aspect_w, aspect_h, aspect_label).run()


if __name__ == "__main__":
    main()
