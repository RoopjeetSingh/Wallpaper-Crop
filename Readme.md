<h1 align="center">Wallpaper Crop</h1>

<p align="center">
  <strong>A lightweight manual cropper for turning wide movie stills into wallpapers.</strong>
</p>

<p align="center">
  <a href="./LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
</p>

Wallpaper Crop opens images one by one and crops each to a chosen aspect ratio. The height does not change but the width is cut based on the given aspect ratio. It was made so that I could convert movie screenshots into laptop wallpapers.

## How it works

* Each image is shown full-frame.
* A click near the left edge becomes the left border, when there is not enough room to place the crop to the left of that point.
* A click near the right edge becomes the right border, when there is not enough room to place the crop to the right of that point.
* If the click can sit in the middle, or cannot be either edge, it is the center of the crop.
* The box is drawn over the image. Clicking Enter crops and saves the cropped image and loads the next image.

## Features

- [x] One image at a time, with a red `x/y` counter at the top left displaying the number of images cropped / total images
- [x] Height is never cropped, only the width
- [x] Click to set the left edge, right edge, or center
- [x] Clicking Enter without using your mouse previews a centered crop, clicking enter again crops and saves the cropped image
- [x] Esc clears the box so that you can crop again
- [x] Right arrow postpones an image until the end
- [x] Left arrow goes back to recrop, and confirming overwrites the previously cropped image
- [x] Already cropped images are skipped on the next run of the same folder
- [x] User is asked for the Aspect ratio, source folder, and output folder but you can keep the default values

## Install

Requires Python 3.

```bash
pip3 install Pillow
```

## Usage

```bash
python3 crop_tool.py
```

Press Enter at each prompt to keep the default.

| Prompt | Default | Description |
| --- | --- | --- |
| Aspect ratio | `16:10` | Width:height. Other examples: `16:9`, `21:9` |
| Source folder | `source_images` | Images to crop |
| Output folder | `cropped` | Where cropped files are saved |

If the output folder already has a file with the same name as a source image, that image is not shown. If you had 100 images to crop, had to go somewhere after the 60th image, and then came back and reran the tool, it would start from the 61st image.

### Controls

| Key | Action |
| --- | --- |
| Click | Place the crop. Left side is the left border, right side is the right border, middle is the center |
| Enter | With no box, show a centered crop. With a box, save and open the next image |
| Esc | Clear the box |
| Right arrow | Postpone the current image to the end. The counter does not advance. After going back, it moves forward again |
| Left arrow | Show the previous image so that we can recrop it |

The red counter is `x/y`: the current image number and the total number of images. Skipping does not increase `x`.

## Results

Sample stills from *Spider-Man: Across the Spider-Verse*, cropped to 16:10. Sources are in `source_images`, crops in `cropped`. The stills are from [this collection of 4K screenshots](https://www.reddit.com/r/IntoTheSpiderverse/comments/15t18ri/i_took_over_8000_4k_screenshots_of_across_the/).

| Original | Cropped |
| --- | --- |
| <img alt="Original still" width="420" src="source_images/Spider-Man Across the Spider-Verse (4K).mkv_snapshot_00.00.01_[2023.08.09_01.41.44].jpg"> | <img alt="Cropped still" width="420" src="cropped/Spider-Man Across the Spider-Verse (4K).mkv_snapshot_00.00.01_[2023.08.09_01.41.44].jpg"> |
| <img alt="Original still" width="420" src="source_images/Spider-Man Across the Spider-Verse (4K).mkv_snapshot_00.00.01_[2023.08.09_02.24.57].jpg"> | <img alt="Cropped still" width="420" src="cropped/Spider-Man Across the Spider-Verse (4K).mkv_snapshot_00.00.01_[2023.08.09_02.24.57].jpg"> |
| <img alt="Original still" width="420" src="source_images/Spider-Man Across the Spider-Verse (4K).mkv_snapshot_00.00.01_[2023.08.09_02.25.18].jpg"> | <img alt="Cropped still" width="420" src="cropped/Spider-Man Across the Spider-Verse (4K).mkv_snapshot_00.00.01_[2023.08.09_02.25.18].jpg"> |

## Demo

  <video src="https://github.com/user-attachments/assets/09ddfe65-2148-49bf-b36f-6c4127ebc16b" width="720" controls></video>
  Demo video

## Background

I had around 100 movie stills and wanted them as wallpapers. I tried to find tools that can help crop all my stills. I had around 100 images and I didn't want to waste a bunch of time. 

One tool I found was https://github.com/esimov/caire. The tool removes the least important parts of the image. While this is a great tool for some other purpose, it was horrible for a wallpaper since the image looked so distorted.

So I quickly built Wallpaper Crop. Most movie shots are already centered, so Enter is often enough to speedrun through all the cropped images. The 100 stills only took about a minute to crop.

## Author

Roopjeet Singh

## License

Copyright © 2026 Roopjeet Singh

This project is under the MIT License. See the [LICENSE](./LICENSE) file for the full license text.
