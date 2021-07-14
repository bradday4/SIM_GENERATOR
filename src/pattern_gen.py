#!/usr/bin/env python
# TODO Add documentation
# TODO Finish Type Hints
# TODO Release to pypi

__author__ = "Brad Day"
__email__ = "bradday4@gmail.com"
__license__ = "MIT"
import os
import sys
import pathlib
from functools import partial
from typing import Optional, Tuple, Union
import numpy as np
import fire
from scipy import signal
from PIL import Image

FILEFORMATS = frozenset(["tif", "tiff", "jpg", "jpeg", "bmp", "png"])
DEFAULTBAR = "sine"
BARTYPES = {
    "solid": signal.square,
    DEFAULTBAR: np.sin,
    "triangle": partial(signal.sawtooth, width=0.5),
}
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


def func_dispatcher(t: np.ndarray, bar_type: str):

    func = BARTYPES[bar_type]
    return func(t)


def verify_output_dir(output_directory: Union[str, None]) -> str:
    # check the directory exists
    if output_directory:
        if not os.path.exists(output_directory):
            raise ValueError(f"Output directory {output_directory} doesn't exist")
    else:
        if getattr(sys, "frozen", False):
            parent = os.path.dirname(sys.executable)
        elif __file__:
            parent = pathlib.Path(__file__).parent.absolute()

        output_directory = os.path.join(parent, "patterns")
        if not os.path.exists(output_directory):
            os.mkdir(output_directory)
        print(
            f"\nNo Output directory given using {output_directory} for patterned images\n"
        )
    return output_directory


class PatternGenerator:
    def __init__() -> None:
        # PatternGenerator class wraps runner method allowing import in other modules
        pass

    @staticmethod
    def runner(
        *args: Optional[Tuple[int, int, int]],
        bar_type: Optional[str] = "solid",
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

        if bar_type not in BARTYPES:
            raise ValueError(
                f"Bar type must be one of {BARTYPES.keys()} but '{bar_type}' was given"
            )

        if orientation not in ORIENTATION:
            raise ValueError(
                f"Orientation must be either {ORIENTATION} but '{orientation}' was given"
            )

        # check file formats are recognized
        if file_format not in FILEFORMATS:
            raise ValueError(f"File format {file_format} not recognized")

        output_directory = verify_output_dir(output_directory)

        # check bit depth is correct
        if bits not in BITDEPTH:
            raise ValueError(f"Bit depth '{bits}' is not one of {BITDEPTH}")

        # check full_depth is of type bool
        if not isinstance(full_depth, bool):
            raise TypeError(
                f"flag full_depth must be True or False not type {type(full_depth)}"
            )
        # check full_depth is true if bartype is set to anything other than solid
        if bar_type != DEFAULTBAR and not full_depth:
            raise TypeError(f"bar_type {bar_type} only supported in full depth mode")

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

            sig = func_dispatcher(2 * np.pi * freq * t + phi, bar_type)
            sig = rescale(sig, lims=lims)
            sig = cast(sig, DTYPES[bits])

            image = gen_pattern_image(sig, orientation, tile_dim(orientation),)
            # x = np.sin(2 * np.pi * freq * t + phi)
            # x = rescale(x)
            # image = gen_pattern_image(x, orientation, what_dim(orientation))

            image.save(
                os.path.join(output_directory, f"phi_{i+1:02d}.{extension}"),
                file_format,
            )


if __name__ == "__main__":
    fire.Fire(PatternGenerator.runner)
#%%
# %%
