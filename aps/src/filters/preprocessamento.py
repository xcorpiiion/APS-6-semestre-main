import itertools
import cv2 as cv
import numpy as np
from scipy.ndimage import rotate
from scipy.ndimage.morphology import binary_hit_or_miss
from scipy.signal import argrelextrema
from skimage.morphology import skeletonize
from src.filters import filter


def normalize(image: np.array,
              low: int,
              upp: int,
              dtype=np.float32):
    return cv.normalize(np.float32(image), None, low, upp,
                        cv.NORM_MINMAX).astype(dtype)


def standartize(image: np.array):
    return (image - np.mean(image)) / np.std(image)


def equalize(image: np.array):
    return cv.equalizeHist(image)


def resize(image: np.array,
           width: int = None,
           height: int = None):
    rows, cols = image.shape

    if width and height:
        return cv.resize(image, (width, height))
    elif width:
        return cv.resize(image, (width, int(width * rows / cols)))
    elif height:
        return cv.resize(image, (int(height * cols / rows), height))
    else:
        return image


def mask(image: np.array,
         blksize: int):
    mask = normalize(image, 0, 255, dtype=np.uint8)

    threshold = np.mean(image) / 2

    for y in range(0, mask.shape[1], blksize):
        for x in range(0, mask.shape[0], blksize):
            blk = mask[x:x + blksize, y:y + blksize]
            mask[x:x + blksize, y:y + blksize] = np.var(blk) > threshold

    contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cv.fillPoly(mask, pts=[max(contours, key=cv.contourArea)], color=(1, 1))

    krnsize = blksize + 1 if blksize % 2 == 0 else blksize
    mask = cv.GaussianBlur(mask, (krnsize * 3, krnsize * 3), krnsize * 3)

    return mask


def orientation(image: np.array,
                grdsigma: float,
                blksigma: float,
                smtsigma: float):
    Gx = filter.filter(image, 'sobelx', int(3 * grdsigma))
    Gy = filter.filter(image, 'sobely', int(3 * grdsigma))

    Gxx = filter.filter(Gx * Gx, 'lowpass', int(3 * blksigma), blksigma)
    Gyy = filter.filter(Gy * Gy, 'lowpass', int(3 * blksigma), blksigma)
    Gxy = filter.filter(Gx * Gy, 'lowpass', int(3 * blksigma), blksigma)

    sin = filter.filter(2 * Gxy, 'lowpass', int(3 * smtsigma), smtsigma)
    cos = filter.filter(Gxx - Gyy, 'lowpass', int(3 * smtsigma), smtsigma)

    orient = np.arctan2(sin, cos) / 2 + np.pi / 2
    return orient


def angles(orient: np.array,
           blksize: int):
    angles = np.zeros(orient.shape)
    for j in range(0, orient.shape[1], blksize):
        for i in range(0, orient.shape[0], blksize):
            angles[i - blksize:i + blksize, j - blksize:j + blksize] =\
                _orientblk_angle(orient, (i, j), blksize)
    return angles


def poincare(angles: np.array,
             blksize: int):
    idx = [(1, 0), (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0)]

    def fpidx(b): return np.sum([b[k2] - b[k1]
                                 for k1, k2 in zip(idx, idx[1:])])

    angles_scaled = np.zeros(tuple(int(x / blksize) for x in angles.shape))
    if (blksize > 1):
        for i in range(0, angles_scaled.shape[0]):
            for j in range(0, angles_scaled.shape[1]):
                angles_scaled[i, j] = np.mean(
                    angles[i * blksize:(i + 1) * blksize,
                           j * blksize:(j + 1) * blksize])

    pidx = np.zeros(angles.shape)
    for i in range(1, angles_scaled.shape[0] - 1):
        for j in range(1, angles_scaled.shape[1] - 1):
            blk = angles_scaled[i - 1:i + 2, j - 1:j + 2]
            pidx[(i - 1) * blksize:(i + 2) * blksize,
                 (j - 1) * blksize:(j + 2) * blksize] = fpidx(blk)
    return pidx


def angular_coherence(angles: np.array,
                      blksize: int,
                      wndsize: int):
    angles_scaled = np.zeros(tuple(int(x / blksize) for x in angles.shape))
    h, w = angles_scaled.shape
    if (blksize > 1):
        for i in range(0, h):
            for j in range(0, w):
                angles_scaled[i, j] = np.mean(
                    angles[i * blksize:(i + 1) * blksize,
                           j * blksize:(j + 1) * blksize])

    hlfwnd = int(np.floor(wndsize / 2))

    angcoh = np.zeros(angles.shape)
    for i in range(0, h):
        for j in range(0, w):
            i1, i2 = np.max((0, i - hlfwnd)), np.min((i + hlfwnd + 1, h))
            j1, j2 = np.max((0, j - hlfwnd)), np.min((j + hlfwnd + 1, w))

            blk = angles_scaled[i1:i2, j1:j2]

            cossum = -1
            for val in np.nditer(blk):
                cossum += np.cos(angles_scaled[i, j] - val)

            angcoh[i * blksize:(i + 1) * blksize,
                   j * blksize:(j + 1) * blksize] = cossum
    return angcoh


def _orientblk_angle(orient: np.array,
                     point: tuple,
                     blksize: int):
    i, j = point
    i1, i2 = np.max([i - blksize, 0]), np.min([i + blksize, orient.shape[0]])
    j1, j2 = np.max([j - blksize, 0]), np.min([j + blksize, orient.shape[1]])
    blk = orient[i1:i2, j1:j2]

    sin = np.mean(np.sin(2 * blk))
    cos = np.mean(np.cos(2 * blk))
    return np.round(np.rad2deg(np.arctan2(sin, cos) / 2), 2)


def frequency(image: np.array,
              orient: np.array,
              blksize: int):
    freq = 1 - normalize(image, 0, 1)

    for y in range(0, image.shape[1], blksize):
        for x in range(0, image.shape[0], blksize):
            blkor = orient[x:x + blksize, y:y + blksize]
            blkim = freq[x:x + blksize, y:y + blksize]
            freq[x:x + blksize, y:y + blksize] = _freq(blkim, blkor)

    return freq


def _freq(image: np.array,
          orient: np.array):
    sin = np.mean(np.sin(2 * orient))
    cos = np.mean(np.cos(2 * orient))
    angle = np.arctan2(sin, cos) / 2

    rot = rotate(image, np.rad2deg(angle) + 90, reshape=True)

    nonzero = np.count_nonzero(rot, axis=0)
    nonzero[nonzero == 0] = 1

    prj = np.sum(rot, axis=0) / nonzero

    prj[prj < np.mean(prj)] = 0

    peaks = argrelextrema(prj, np.greater, order=3)[0]
    n_peaks = len(peaks)

    if n_peaks == 1:
        return 1 / np.max((peaks[0], rot.shape[0] - peaks[0]))

    return n_peaks / (peaks[n_peaks - 1] - peaks[0]) if n_peaks != 0 else 0


def skeleton(image: np.array):
    return skeletonize(image)


def prune(sklt: np.array,
          windows: np.array,
          iters: int = 1):
    pruned = np.array(sklt)
    for _ in itertools.repeat(None, iters):
        for wnd in windows:
            pruned[binary_hit_or_miss(pruned, wnd)] = 0

    return pruned


def fillholes(image: np.array,
              hole_value: bool = 0):
    image_filled = np.array(image)
    for i in range(1, image.shape[0] - 1):
        for j in range(1, image.shape[1] - 1):
            if image[i, j] == hole_value and\
               not image[i + 1, j] == hole_value and\
               not image[i - 1, j] == hole_value and\
               not image[i, j + 1] == hole_value and\
               not image[i, j - 1] == hole_value:
                image_filled[i, j] = not hole_value
    return image_filled
