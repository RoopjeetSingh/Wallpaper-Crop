# Wallpaper crop

Wallpaper crop is a super lightweight and simple tool that can be used to crop images for wallpapers (it was primarily made for cropping images from movies to set them as your laptop wallpaper)

Crops images one by one to a chosen aspect ratio. Height stays full; only the width is cropped.

Usually you would just be able to click enter to crop the image on the center, since most shots in movies are shot to be centered. However, not all. For my 100 images, it took me 1 minute to crop!

## Setup

```bash
pip3 install Pillow
```

## Run

```bash
python3 crop_tool.py
```

Press Enter at each prompt to keep the default.

- **Aspect ratio** — `16:10`. Other examples: `16:9`, `21:9`.
- **Source folder** — `source_images`.
- **Output folder** — `cropped`.

If you were using this tool on a folder with 100 images and had to go do something else after 60 images. Rerunning the tool would start from the 61st image, skipping the images you have already done. 
The way this works is if a output folder already has a file with the same name as a file in the source folder, that file/image is not shown.

## Controls

A red counter shows `x/y`: the current image number and the total. Skipping does not increase x.

- **Click** to place the crop. A click near the left edge is the left border, near the right edge is the right border, and in the middle is the center.
- **Enter** with no box shows a centered crop. **Enter** again saves it and opens the next image.
- **Esc** clears the box so you can click again.
- **Right arrow** postpones the current image to the end. After going back, it moves forward again.
- **Left arrow** shows the previous image to recrop it. Cropping again overwrites the previously cropped file.

## Background
I tried to find tools that can help crop my wallpaper. I had around 100 images and I didn't want to waste a bunch of time. 
One tool I found was https://github.com/esimov/caire. The tool removes the least important parts of the image. While this is a great tool for some other purpose, it was horrible for a wallpaper since the image looked so distorted.

I knew I had to create my own. And this is where AI shined. I vibe coded for the win!

Starting with 
"Create a tool which opens an application, showing me the images in @wallpaper-full-images one by one. Each image gets cropped to 16:10 ratio where the height never gets cropped, only the width does. The way the cropping works is I click by my mouse somewhere and if this is on the left side (checked by seeing if its not possible to have the corresponding width on the left, that means we are on the left), the crop happens by taking that as the left border, if it is on the right side (similarly checked) the crop happens by taking it as the right side. And if both sides are not possible, that mouse click is treated as the center of the crop.
After the mouse is clicked somewhere, it shows the box and clicking enter would crop the image and show the next image.
Basically manual cropping just easier.

Also make it so if you don't click anywhere and just click enter, it just takes the center directly for cropping. 
When a box is shown, clicking esc key should stop showing the box so that the user can click for crop again."

A slight bug fix
"Enter With no click should not use a centered crop immediately and instead show the box like always
Also the file should ensure that if I start it again in the future, it doesn't show me the images I have already cropped"

Minor improvements
"can you make it so the tool asks the person for the aspect ratio (but keep the default value so if someone just does enter, the default value is selected), SOURCE_DIR and OUTPUT_DIR
"

And some more minor improvements
"can you also add a keybind to right arrow key to skip an image for now and show it at the end and left arrow key if we cropped something and want to recrop it (this would overwrite the previous image if we go ahead with cropping and don't just close it). And a counter with red color that shows x/y where x is image number and y is total images (skipping an image does not change the counter since that image was not cropped, just postponed)
"

And I had my Wallpaper crop tool!