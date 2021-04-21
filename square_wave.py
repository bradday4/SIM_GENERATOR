#%%
from skimage.io import imsave
from skimage import img_as_ubyte
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

# %%
def gen_pattern_image(signal, height):
    return np.tile(signal[np.newaxis, :], (height, 1))


def rescale(x, lims=(0, 1)):
    new_min, new_max = lims
    old_min, old_max = np.min(x), np.max(x)
    return (new_max - new_min) * ((x - old_min) / (old_max - old_min)) + new_min


# lh : number of vertical elements on the optical device
# lv : number of horizontal elements on the optical device

# SLM
# lh = 1536
# lv = 2048

# DMD
lh = 912
lv = 1140

wl = 4  # (width of line in pixels)
freq = lv / wl / 2
# phi_deg = [0.001, 72.0, -72.0, 60.0, -60.0] # non uniform
phi_deg = [0.001, 72.0, 144, 216, 288]  # uniform (can't handle 0 or 360)
# phi_deg = [0.000, 144.0, -144.0]  # non uniform
phi_rad = (np.radians(deg) for deg in phi_deg)  # phase in radian
t = np.linspace(0, 1, lv, endpoint=False)
ims = []
for phi in phi_rad:
    # ims.append(gen_pattern_image(signal.square(2 * np.pi * freq * t + phi), lh))
    x = np.sin(2 * np.pi * freq * t + phi)
    x = rescale(x)

    ims.append(gen_pattern_image(x, lh))
    # plt.plot(t * 2048, signal.square(2 * np.pi * freq * t + phi))
    # plt.ylim(-2, 2)


# %%
for i, im in enumerate(ims):
    imsave(
        r"C:\Users\Brad\Desktop\eq_sine\vsine_f{freq:.0f}pix_{i}.bmp".format(
            freq=wl, i=i
        ),
        img_as_ubyte(im),
    )
# %%
