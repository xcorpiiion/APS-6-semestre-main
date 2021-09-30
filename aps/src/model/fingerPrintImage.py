import random

import cv2 as cv
import numpy as np


class FingerprintImage:

    def __init__(self,
                 id: int,
                 number: int,
                 fppath: str):
        self.id = id
        self.number = number
        self.fppath = fppath

    def __eq__(self, other):
        return self.id == other.id and self.number == other.number

    def __lt__(self, other):
        if self.id == other.id:
            return self.number < other.number
        else:
            return self.id < other.id

    def getData(self,
                colorspace: int = cv.IMREAD_GRAYSCALE,
                astype: int = np.uint8):
        return cv.imread(self.fppath, colorspace).astype(astype)


def readOne(fppath: str):
    id = random.randrange(200, 500)
    number = random.randrange(1, 199)

    return FingerprintImage(id, number, fppath)
