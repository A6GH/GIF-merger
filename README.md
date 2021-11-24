# GIF merger

This is a python3 program that merges multiple GIFs into a single canvas. Each GIF can be rotated by an arbitrary angle and positioned with an arbitrary offset from the top left corner of the canvas. The program searches for GIFs in the `./gifs` folder based on the specified file names in the `./gif_params.json` file. Apart from the file names, the user must specify the horizontal and vertical offsets (in pixels) and rotation angles (in degrees) for each GIF.

GIF merger can merge input GIFs in three different ways:

1) Duration of the merged GIF will equal the maximum duration among the individual GIFs, where the individual GIFs of lower duration are stopped until the end of the longest individual GIF within the merged GIF is reached
2) Duration of the merged GIF will equal the maximum duration among the individual GIFs, where the individual GIFs of lower duration are looped until the end of the longest individual GIF within the merged GIF is reached
3) Duration of the merged GIF will equal the least common multiple of individual GIFs\' durations, so that the individual GIFs within the merged GIF have seamless loops (pick with caution, can result in a memory leak or very big merged GIF size)

Apart from specifying the GIF merger mode at the program start, the user can specify the number of times the merged GIF should loop. Specifying `0` means that it will loop forever.

The merged GIF is saved to the `merged.gif` file in `./gifs` folder by default.