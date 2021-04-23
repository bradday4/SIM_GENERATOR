# SIM_GENERATOR

A little command line utility to generate pattern images for structured illumination microscopy

## Installation

Head over to the [release](https://github.com/bradday4/SIM_GENERATOR/releases) page and download the latest executable `pattern_gen.exe`.

## Usage

### Minimum usage

From the directory that `pattern_gen.exe` is in

```Shell
pattern_gen <image_height> <image_width> <pattern_bar_width> --phase_shifts <n_shifts>
```

### Example with all arguments

```Shell
pattern_gen 256 256 16 --phase_shifts 3 --output_directory D:\SIM_GENERATOR\DemoPatterns --orientation horizontal --file_format jpg --bits 8 --full_depth True
```

Will generate the following images
|phi_01.jpg |phi_02.jpg |phi_03.jpg|
|--- |---|---|
|![](https://github.com/bradday4/SIM_GENERATOR/blob/main/DemoPatterns/phi_01.jpg) |![](https://github.com/bradday4/SIM_GENERATOR/blob/main/DemoPatterns/phi_02.jpg) |![](https://github.com/bradday4/SIM_GENERATOR/blob/main/DemoPatterns/phi_03.jpg)|

| Argument         | Type          | Optional? | Default                  | Options                     | Desc                                                                                                                         | Example                                    |
| ---------------- | ------------- | --------- | ------------------------ | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| Positional Args  | (int int int) | False     | NONE                     | NONE                        | Image Height, Image Width, & Bar width                                                                                       | `1024 986 32`                              |
| phase shifts     | int           | False     | NONE                     | `0<n<inf`                   | How many phase shift images                                                                                                  | `--phase_shifts 5 `                        |
| output directory | str           | True      | `~exe location\patterns` |                             | where to save pattern images                                                                                                 | `--output_directory C:\Users\Thanos\Stuff` |
| orientation      | str           | True      | `vertical`               | `vertical` or `horizontal`  | which way should the bars be oriented                                                                                        | `--orientation vertical`                   |
| file format      | str           | True      | `bmp`                    | `bmp tiff tif jpg jpeg png` | File type                                                                                                                    | `--file_format tif`                        |
| bits             | int           | True      | `8`                      | `8 16 32`                   | Bit depth of image                                                                                                           | `--bits 16`                                |
| full depth       | bool          | True      | `True`                   | `True False`                | If true Use full range of bitdepth e.g 255 for `8` otherwise image will be 0 or 1. When `bits==32` option overides to`False` | `--full_depth True`                        |
| bar type         | str           | True      | `solid`                  | `solid triangle sine`       | Type of waveform                                                                                                             | `--bar_type sine`                          |

## Requests

If you have a feauture request open an issue and let me know.
