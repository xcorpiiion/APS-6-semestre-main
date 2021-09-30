import cv2 as cv
import numpy as np
from scipy.signal import convolve2d
from scipy.ndimage import rotate


def filter(image: np.array,
           method: str = None,
           krnsize: int = 11,
           krnsigma: int = 2,
           krn: np.array = None):

    if method is None and krn is not None:
        return _filter_custom(image, krn)
    elif method == 'lowpass':
        return _filter_lowpass(image, krnsize, krnsigma)
    elif method == 'sobelx':
        return _filter_sobel(image, 'x', krnsize)
    elif method == 'sobely':
        return _filter_sobel(image, 'y', krnsize)
    else:
        raise Exception(method + ' filtering method is not supported!')


def _filter_custom(image: np.array,
                   krn: np.array):
    assert(krn.shape[0] == krn.shape[1])
    return convolve2d(image.astype(np.float32), krn, mode='same')


def _filter_sobel(image: np.array,
                  axis: str,
                  krnsize: int):
    assert(axis == 'x' or axis == 'y')
    if axis == 'x':
        return cv.Sobel(image.astype(np.float32), cv.CV_32F, 1, 0,
                        ksize=krnsize)
    elif axis == 'y':
        return cv.Sobel(image.astype(np.float32), cv.CV_32F, 0, 1,
                        ksize=krnsize)


def _filter_lowpass(image: np.array,
                    krnsize: int,
                    krnsigma: float):
    krn = cv.getGaussianKernel(krnsize, krnsigma)
    krn = krn * krn.T
    return _filter_custom(image, krn)


def medgabor(image: np.array,
             orient: np.array,
             freq: np.array):
    medfreq = np.round(np.median(freq[freq > 0]), 2)
    sigma_x = 0.66 / medfreq
    sigma_y = 0.66 / medfreq

    krnsize = int(np.round(3 * np.max([sigma_x, sigma_y])))
    x, y = np.meshgrid(np.linspace(-krnsize, krnsize, (2 * krnsize + 1)),
                       np.linspace(-krnsize, krnsize, (2 * krnsize + 1)))

    original_gab = np.exp(-(x**2 / sigma_x**2 + y**2 / sigma_y**2)) *\
        np.cos(2 * np.pi * medfreq * x)

    d_angle = 3
    n_filters = int(180 / d_angle)

    fbank = np.zeros((n_filters, original_gab.shape[0], original_gab.shape[1]))
    for o in range(0, n_filters):
        fbank[o] = rotate(original_gab, -(o * d_angle + 90), reshape=False)

    validr, validc = np.array(np.where(freq != 0))
    padimage = np.pad(image, krnsize, constant_values=0)

    gab_idx = np.round(orient * n_filters / np.pi)
    gab_idx[gab_idx < 1] += n_filters
    gab_idx[gab_idx > n_filters] -= n_filters

    flt = np.zeros(image.shape, dtype=np.float32)

    for k in range(0, len(validr)):
        r = validr[k] + krnsize
        c = validc[k] + krnsize

        gab = fbank[int(gab_idx[r - krnsize][c - krnsize] - 1)]
        blk = padimage[r - krnsize:r + krnsize + 1,
                       c - krnsize:c + krnsize + 1]
        flt[r - krnsize][c - krnsize] = np.sum(blk * gab)

    return flt
