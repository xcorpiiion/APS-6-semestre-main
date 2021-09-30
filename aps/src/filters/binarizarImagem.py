import cv2 as cv


def binarizar(img):
    _, imagem = cv.threshold(img, 0, 1, cv.THRESH_BINARY + cv.THRESH_OTSU)
    return imagem
