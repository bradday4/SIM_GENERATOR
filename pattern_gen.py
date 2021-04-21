#!/usr/bin/env python
__author__ = "Brad Day"
__email__ = "bradday4@gmail.com"
__license__ = "MIT"
import os
import pathlib
from typing import Optional, Tuple
import numpy as np
import fire
from scipy import signal
from PIL import Image

FILEFORMATS = frozenset(["tif", "tiff", "tif", "jpg", "jpeg", "bmp", "png"])
ORIENTATION = frozenset(["vertical", "horizontal"])
DEVICEDEFAULTS = (1024, 1024, 8)
# lv: int,
# lh: int,
# wb: int,


def gen_pattern_image(sig, orientation, size) -> Image:
    if orientation == "horizontal":
        return Image.fromarray(np.tile(sig[:, np.newaxis], (1, size)))
    else:
        return Image.fromarray(np.tile(sig[np.newaxis, :], (size, 1)))


def rescale(x, lims=(0, 1)):
    new_min, new_max = lims
    old_min, old_max = np.min(x), np.max(x)
    return (new_max - new_min) * ((x - old_min) / (old_max - old_min)) + new_min


def main(
    *args: Optional[Tuple[int, int, int]],
    orientation: str = "vertical",
    file_format: str = "bmp",
    shifts: int = 3,
    output_directory: Optional[str] = None,
):
    # unpack the arguments:
    # if zero provided use defaults
    # if 3 are given unpack them else raise an error
    if args:
        if len(args) != 3:
            raise TypeError(f"Expected 3 arguments but {len(args)} were given")
        elif not all((isinstance(arg, int) for arg in args)):
            raise TypeError(f"Args must be of type int")
        lv, lh, wb = args
    else:
        lv, lh, wb = DEVICEDEFAULTS

    if orientation not in ORIENTATION:
        raise ValueError(
            f"Orientation must be either {ORIENTATION} but '{orientation}' was given"
        )

    # check file formats are recognized
    if file_format not in FILEFORMATS:
        raise ValueError(f"File format {file_format} not recognized")

    # check the directory exists
    if output_directory:
        if not os.path.exists(output_directory):
            raise ValueError(f"Output directory {output_directory} doesn't exist")
    else:
        parent = pathlib.Path(__file__).parent.absolute()
        output_directory = os.path.join(parent, "patterns")
        if not os.path.exists(output_directory):
            os.mkdir(output_directory)
        print(
            f"\nNo Output directory given using {output_directory} for patterned images\n"
        )

    what_dim = lambda x: lh if x == "vertical" else lv
    tile_dim = lambda x: lv if x == "vertical" else lh
    freq = what_dim(orientation) / wb / 2

    # phi_deg = [0.001, 72.0, 144, 216, 288]  # uniform (can't handle 0 or 360)
    phi_deg = np.linspace(0.001, 360, shifts, endpoint=False)
    phi_rad = (np.radians(deg) for deg in phi_deg)  # phase in radian
    t = np.linspace(0, 1, what_dim(orientation), endpoint=False)  # spacing
    # ims = []
    for i, phi in enumerate(phi_rad):
        image = gen_pattern_image(
            signal.square(2 * np.pi * freq * t + phi),
            orientation,
            tile_dim(orientation),
        )
        # x = np.sin(2 * np.pi * freq * t + phi)
        # x = rescale(x)

        # image = gen_pattern_image(x, orientation, what_dim(orientation))
        image.save(
            os.path.join(output_directory, f"phi_{i+1:02d}.{file_format}"), file_format
        )
        # plt.plot(t * 2048, signal.square(2 * np.pi * freq * t + phi))
        # plt.ylim(-2, 2)


if __name__ == "__main__":
    fire.Fire(main)
