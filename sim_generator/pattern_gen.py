#!/usr/bin/env python
# TODO: Add type hints and doc strings
# TODO: Write Unit Tests
__author__ = "Brad Day"
__email__ = "bradday4@gmail.com"
__license__ = "MIT"
import sys
import os
import argparse
import logging
import numpy as np
from typing import Dict, List, Tuple
from functools import partial
from scipy import signal
from enum import Enum
from pyfiglet import Figlet
from PIL import Image
from pathlib import Path
import tempfile

if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    # application_path = Path(sys._MEIPASS).absolute()
    application_path = Path(sys.executable).parent.absolute()

else:
    application_path = Path(__file__).parent.absolute()

logger = logging.getLogger("pattern_gen")
logger.setLevel(logging.DEBUG)
if application_path.parent.joinpath("logs").exists():
    fh = logging.FileHandler(
        application_path.parent.joinpath("logs/pattern_gen.log")
    )
else:
    fh = logging.FileHandler(
        Path(tempfile.gettempdir()).joinpath("pattern_gen.log")
    )
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


logger.debug(f"application path is : {application_path}")

parser = argparse.ArgumentParser()


class CheckDirAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.exists(values):
            parser.error("Directory {} does not exist".format(values))

        setattr(namespace, self.dest, values)


class MinPixAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values < 1:
            parser.error(
                "Minimum pixel value for {0} is 1 pixel".format(self.dest)
            )

        setattr(namespace, self.dest, values)


class ArgTypeMixin(Enum):
    @classmethod
    def argtype(cls, s: str) -> Enum:
        try:
            return cls[s]
        except KeyError:
            raise argparse.ArgumentTypeError(
                f"{s!r} is not a valid {cls.__name__}"
            )

    def __str__(self):
        return self.name


class FileFormat(ArgTypeMixin, Enum):
    """What type of format to save output images as"""

    tif = "tiff"
    tiff = "tiff"
    jpg = "jpeg"
    jpeg = "jpeg"
    bmp = "bmp"
    png = "png"


class BarFuncType(ArgTypeMixin, Enum):
    """What type of function to generate bars"""

    solid = partial(signal.square)
    sine = partial(np.sin)
    triangle = partial(signal.sawtooth, width=0)

    def __call__(self, *args, **kwargs) -> partial:
        return self.value(*args, **kwargs)


class Orientation(ArgTypeMixin, Enum):
    """What type of orientation to use"""

    horizontal = 0
    vertical = 1


parser.add_argument(
    "image_dims",
    type=int,
    nargs=2,
    choices=range(256, 2049),
    metavar="[256-2048]",
    help="Output Dimension of the Image. H x W Muse be between 256 - 2048",
)

parser.add_argument(
    "bar_size",
    type=int,
    nargs="?",
    action=MinPixAction,
    help="Size of the bars",
)

parser.add_argument(
    "--phase_shifts",
    type=int,
    default=3,
    choices=range(3, 13),
    metavar="[3-12]",
    help="Number of Phase Shifts",
)

parser.add_argument(
    "--file_format",
    type=FileFormat.argtype,
    choices=FileFormat,
    default="bmp",
    help="File format to save image as",
)
parser.add_argument(
    "--bar_func",
    type=BarFuncType.argtype,
    choices=BarFuncType,
    default="sine",
    help="Function that generates Bars",
)
parser.add_argument(
    "--orientation",
    type=Orientation.argtype,
    choices=Orientation,
    default="vertical",
    help="Vertical or Horizontal Bars",
)
parser.add_argument(
    "--bit_depth",
    type=str,
    choices=("8", "16", "32"),
    default="8",
    help="Bit Depth of the image",
)
parser.add_argument(
    "--output_directory",
    type=str,
    default=application_path,
    action=CheckDirAction,
    metavar="",
    help="Directory to save images to. Defaults to current path of __file__",
)

parser.add_argument(
    "--full_depth",
    type=bool,
    default=True,
    metavar="{True, False}",
    help="Use full bit depth range",
)


class SimGenerator:
    __slots__ = [
        "image_dims",
        "bar_size",
        "phase_shifts",
        "file_format",
        "bar_func",
        "orientation",
        "bit_depth",
        "output_directory",
        "full_depth",
        "DTYPES",
        "BITLIMS",
    ]
    image_dims: List[int]
    bar_size: int
    phase_shifts: int
    file_format: FileFormat
    bar_func: BarFuncType
    orientation: Orientation
    bit_depth: str
    output_directory: str
    full_depth: bool
    DTYPES: Dict
    BITLIMS: Dict

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.DTYPES = {"8": np.uint8, "16": np.uint16, "32": np.uint32}
        self.BITLIMS = {"8": (0, 255), "16": (0, 65535), "32": (0, 4294967295)}

    def __repr__(self) -> str:
        return str({slot: getattr(self, slot) for slot in self.__slots__})

    def __len__(self):
        return len(self.__slots__)

    def _what_dim(self):
        """Return Vertical or Horizontal image dimension based on Orientation"""
        lv = self.image_dims[0]  # Vertical
        lh = self.image_dims[1]  # Horizontal
        return lh if self.orientation.name == "vertical" else lv

    def _tile_dim(self):
        """Return Vertical or Horizontal image dimension based on Orientation"""
        lv = self.image_dims[0]  # Vertical
        lh = self.image_dims[1]  # Horizontal
        return lv if self.orientation.name == "vertical" else lh

    def _get_freq(self) -> float:
        """Find the frequency of the bar function"""
        freq = self._what_dim() / self.bar_size / 2
        logger.debug(f"Frequency: {freq} pixels")
        return freq

    def _gen_phi(self):
        """Create 1d signal of size n"""

        phi_deg = np.linspace(0.001, 360, self.phase_shifts, endpoint=False)
        return (
            np.radians(deg) for deg in phi_deg
        )  # phase in radian generator

    def _gen_signal(self, phi):
        # todo: generate t outside of this function
        t = np.linspace(0, 1, self._what_dim(), endpoint=False)  # spacing

        freq = self._get_freq()
        sig = self.bar_func(2 * np.pi * freq * t + phi)
        sig = self._rescale(sig, self.BITLIMS[self.bit_depth])
        sig = self._cast(sig, self.DTYPES[self.bit_depth])
        return sig

    def _rescale(self, x, lims=(0, 1)):
        new_min, new_max = lims
        old_min, old_max = np.min(x), np.max(x)
        return (new_max - new_min) * (
            (x - old_min) / (old_max - old_min)
        ) + new_min

    def _cast(self, x: np.array, dtype: np.dtype):
        return x.astype(dtype)

    def _save_images(self, images: List[Tuple[int, Image.Image]]):
        """Save the image to disk"""
        for i, image in images:
            _path = os.path.join(
                self.output_directory,
                f"phi_{i+1:02d}.{self.file_format.value}",
            )
            image.save(_path, self.file_format.value)
            logger.info(f"Image saved to {_path}")

    def _make_pattern_image(self, sig: np.array) -> Image.Image:
        if self.orientation.name == "horizontal":
            return Image.fromarray(
                np.tile(sig[:, np.newaxis], (1, self._tile_dim()))
            )
        else:
            return Image.fromarray(
                np.tile(sig[np.newaxis, :], (self._tile_dim(), 1))
            )

    def run(self):
        """Run the simulation"""
        phis = self._gen_phi()
        images = list()
        for i, phi in enumerate(phis):
            sig = self._gen_signal(phi)
            images.append((i, self._make_pattern_image(sig)))

        self._save_images(images)


def arg_logger(args):
    for arg, value in sorted(vars(args).items()):
        logger.debug("Argument %s: %r", arg, value)


def main():
    custom_fig = Figlet(font="colossal")
    print("\n\n\n", custom_fig.renderText("SIM GEN"))
    # use argparse parser to parse input args
    if not sys.argv[1:]:
        sys.exit(0)
    logger.debug("Sim Generator executed from command line")
    parsed_args = parser.parse_args(sys.argv[1:])
    arg_logger(parsed_args)
    sg = SimGenerator(**vars(parsed_args))
    sg.run()


if __name__ == "__main__":
    main()
