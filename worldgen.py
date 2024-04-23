from matplotlib import pyplot as plt
from perlin_noise import PerlinNoise
import numpy as np

def get_elevation(size):
    xpix, ypix = size
    noise = PerlinNoise(octaves=50, seed=4426)
    scale = (1/3, 1/3)
    elevation = np.array(
        [
            [noise([(x / xpix) * scale[0], (y / ypix) * scale[1]]) for y in range(ypix)] for x in range(xpix)
        ]
    )

    return elevation

def elevation_to_rgba(elevation, cmap='gist_earth'):
    xpix, ypix = np.array(elevation).shape
    colormap = plt.cm.get_cmap(cmap)
    elevation = (elevation - elevation.min())/(elevation.max()-elevation.min())
    ''' You can play around with colormap to get a landscape of your preference if you want '''
    landscape = np.array([colormap(elevation[i, j])[0:3] for i in range(xpix) for j in range(ypix)]).reshape(xpix, ypix, 3)*255
    landscape = landscape.astype('uint8')
    return landscape