#!/usr/bin/env python3
"""Manual 16:10 cropper — full height retained, width cropped via click."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageTk
import tkinter as tk

ASPECT_W, ASPECT_H = 16, 10
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
SOURCE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SOURCE_DIR / "cropped"


def list_images(folder: Path, output_dir: Path = OUTPUT_DIR) -> list[Path]:
    return sorted(
        p
        for p in folder.iterdir()
        if p.is_file()
        and p.suffix.lower() in IMAGE_EXTS
        and not (output_dir / p.name).exists()
    )


def crop_width_for_height(height: int) -> int:
    return round(height * ASPECT_W / ASPECT_H)


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
    def __init__(self, images: list[Path]) -> None:
        self.images = images
        self.index = 0
        self.crop_box: tuple[int, int, int, int] | None = None  # left, top, right, bottom
        self.pil_image: Image.Image | None = None
        self.display_scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.photo: ImageTk.PhotoImage | None = None

        OUTPUT_DIR.mkdir(exist_ok=True)

        self.root = tk.Tk()
        self.root.title("16:10 Crop Tool")
        self.root.configure(bg="#1a1a1a")
        self.root.minsize(800, 500)

        self.status = tk.Label(
            self.root,
            text="",
            fg="#cccccc",
            bg="#1a1a1a",
            font=("Helvetica", 13),
            pady=8,
        )
        self.status.pack(side=tk.TOP, fill=tk.X)

        self.hint = tk.Label(
            self.root,
            text="Click to place crop  ·  Enter to confirm  ·  Esc to clear box",
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
        self.root.bind("<Return>", self.on_enter)
        self.root.bind("<KP_Enter>", self.on_enter)
        self.root.bind("<Escape>", self.on_escape)

        self.load_current()

    def load_current(self) -> None:
        if self.index >= len(self.images):
            self.status.config(text="Done — all images cropped.")
            self.canvas.delete("all")
            self.pil_image = None
            self.crop_box = None
            return

        path = self.images[self.index]
        self.pil_image = Image.open(path).convert("RGB")
        self.crop_box = None
        self.root.title(f"16:10 Crop Tool — {path.name} ({self.index + 1}/{len(self.images)})")
        self.status.config(
            text=f"{self.index + 1}/{len(self.images)}  ·  {path.name}  ·  "
            f"{self.pil_image.width}×{self.pil_image.height}"
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
        crop_w = crop_width_for_height(ih)
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

    def on_resize(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        self.render()

    def save_and_next(self) -> None:
        if self.pil_image is None or self.crop_box is None:
            return
        path = self.images[self.index]
        cropped = self.pil_image.crop(self.crop_box)
        out = OUTPUT_DIR / path.name
        cropped.save(out, quality=95)
        print(f"Saved {out}  ({cropped.width}×{cropped.height})")
        self.index += 1
        self.load_current()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE_DIR
    images = list_images(folder)
    if not images:
        print(f"No uncropped images left in {folder}")
        sys.exit(0)
    print(f"{len(images)} remaining → cropped into {OUTPUT_DIR}")
    CropApp(images).run()


if __name__ == "__main__":
    main()
