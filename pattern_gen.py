#!/usr/bin/env python
# TODO Add documentation
# TODO Finish Type Hints
# TODO Make CLI executable
# TODO Release to pypi
# TODO Update Readme

__author__ = "Brad Day"
__email__ = "bradday4@gmail.com"
__license__ = "MIT"
import os
import pathlib
from typing import Optional, Tuple
from collections import namedtuple
import numpy as np
import fire
from scipy import signal
from PIL import Image

FILEFORMATS = frozenset(["tif", "tiff", "jpg", "jpeg", "bmp", "png"])
ORIENTATION = frozenset(["vertical", "horizontal"])
DEVICEDEFAULTS = (1024, 1024, 8)
BITDEPTH = frozenset([8, 16, 32])
DTYPES = {8: np.uint8, 16: np.uint16, 32: np.uint32}
BITLIMS = {8: (0, 2 ** 8 - 1), 16: (0, 2 ** 16 - 1), 32: (0, 1)}
FORMATBITPAIRS = {
    "tif": frozenset([8, 16, 32]),
    "tiff": frozenset([8, 16, 32]),
    "jpg": frozenset([8]),
    "jpeg": frozenset([8]),
    "bmp": frozenset([8]),
    "png": frozenset([8, 16]),
}
EXTALIAS = {"tif": "tiff", "jpg": "jpeg"}
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


def cast(x: np.array, dtype: np.dtype):
    return x.astype(dtype)


def main(
    *args: Optional[Tuple[int, int, int]],
    orientation: str = "vertical",
    file_format: str = "bmp",
    phase_shifts: int = 3,
    output_directory: Optional[str] = None,
    bits: Optional[int] = 8,
    full_depth: Optional[bool] = True,
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

    # check bit depth is correct
    if bits not in BITDEPTH:
        raise ValueError(f"Bit depth '{bits}' is not one of {BITDEPTH}")

    # check full_depth is of type bool
    if not isinstance(full_depth, bool):
        raise TypeError(
            f"flag full_depth must be True or False not type {type(full_depth)}"
        )

    # check chosen number of bits is compatabile with image format
    if not bits in FORMATBITPAIRS[file_format]:
        raise ValueError(
            f"File format {file_format} only takes bits {FORMATBITPAIRS[file_format]}"
        )

    # modify extensions
    if file_format in EXTALIAS:
        extension = file_format
        file_format = EXTALIAS[file_format]
    else:
        extension = file_format

    what_dim = lambda x: lh if x == "vertical" else lv
    tile_dim = lambda x: lv if x == "vertical" else lh
    freq = what_dim(orientation) / wb / 2

    phi_deg = np.linspace(0.001, 360, phase_shifts, endpoint=False)
    phi_rad = (np.radians(deg) for deg in phi_deg)  # phase in radian
    t = np.linspace(0, 1, what_dim(orientation), endpoint=False)  # spacing

    if full_depth:
        lims = BITLIMS[bits]
    else:
        lims = (0, 1)

    for i, phi in enumerate(phi_rad):

        sig = signal.square(2 * np.pi * freq * t + phi)
        sig = rescale(sig, lims=lims)
        sig = cast(sig, DTYPES[bits])

        image = gen_pattern_image(
            sig,
            orientation,
            tile_dim(orientation),
        )
        # x = np.sin(2 * np.pi * freq * t + phi)
        # x = rescale(x)
        # image = gen_pattern_image(x, orientation, what_dim(orientation))

        image.save(
            os.path.join(output_directory, f"phi_{i+1:02d}.{extension}"), file_format
        )


if __name__ == "__main__":
    fire.Fire(main)
