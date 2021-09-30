import numpy as np
from src.filters import (binarizarImagem, feature, filter, minucias,
                         preprocessamento)
from src.model import fingerPrintImage


def _prepare(fnp: fingerPrintImage.FingerprintImage):
    img = fnp.getData()
    img = preprocessamento.resize(img, width=400, height=500)

    img = preprocessamento.normalize(img, low=0, upp=255)
    mask = preprocessamento.mask(img, blksize=20)
    nimg = preprocessamento.standartize(img)

    ornt = preprocessamento.orientation(
        nimg, grdsigma=3, blksigma=3, smtsigma=3)

    freq = preprocessamento.frequency(nimg, ornt, blksize=50)
    freq = freq * mask

    prep = filter.medgabor(nimg, ornt, freq)

    prep = 255 - preprocessamento.normalize(prep, 0, 255, np.uint8)
    prep = binarizarImagem.binarizar(prep)
    prep = preprocessamento.fillholes(prep)

    sklt = preprocessamento.skeleton(prep)

    sklt = preprocessamento.prune(sklt,
                                  np.array([
                                      [[1, 0, 0], [0, 1, 0], [0, 0, 0]],
                                      [[0, 1, 0], [0, 1, 0], [0, 0, 0]],
                                      [[0, 0, 1], [0, 1, 0], [0, 0, 0]],
                                      [[0, 0, 0], [0, 1, 1], [0, 0, 0]],
                                      [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
                                      [[0, 0, 0], [0, 1, 0], [0, 0, 1]],
                                      [[0, 0, 0], [0, 1, 0], [0, 1, 0]],
                                      [[0, 0, 0], [0, 1, 0], [1, 0, 0]],
                                      [[0, 0, 0], [1, 1, 0], [0, 0, 0]]
                                  ]), 8)
    sklt = preprocessamento.prune(sklt,
                                  np.array([
                                      [[1, 1, 0], [0, 1, 0], [0, 0, 0]],
                                      [[0, 1, 1], [0, 1, 0], [0, 0, 0]],
                                      [[0, 0, 1], [0, 1, 1], [0, 0, 0]],
                                      [[0, 0, 0], [0, 1, 1], [0, 0, 1]],
                                      [[0, 0, 0], [0, 1, 0], [0, 1, 1]],
                                      [[0, 0, 0], [0, 1, 0], [1, 1, 0]],
                                      [[0, 0, 0], [1, 1, 0], [1, 0, 0]],
                                      [[1, 0, 0], [0, 1, 0], [1, 0, 0]]
                                  ]), 1)
    sklt = preprocessamento.prune(sklt,
                                  np.array([
                                      [[1, 1, 1], [0, 1, 0], [0, 0, 0]],
                                      [[0, 0, 1], [0, 1, 1], [0, 0, 1]],
                                      [[0, 0, 0], [0, 1, 0], [1, 1, 1]],
                                      [[1, 0, 0], [1, 1, 0], [1, 0, 0]],
                                  ]), 1)

    mnte = minucias.minutae(sklt, ornt, remove_invalid=1)

    mnte = np.resize(mnte, (mnte.shape[0] + 1,))
    mnte[mnte.shape[0] - 1] = minucias.core(ornt, mask)

    feat_r = feature.extract(mnte, method='radial', bucketsize=36)
    feat_c = feature.extract(mnte, method='circular', bucketsize=30)

    return nimg, mask, ornt, sklt, mnte, feat_r, feat_c


def enroll(fnp: fingerPrintImage.FingerprintImage):
    nimg, mask, ornt, sklt, mnte, feat_r, feat_c = _prepare(fnp)
    return feat_r, feat_c


def processarImagem(path_image, tipo):
    if tipo == 'cadastro':
        train_fnps = fingerPrintImage.readOne(path_image)

    if tipo == 'login':
        train_fnps = fingerPrintImage.FingerprintImage(0, 0, path_image)

    r, c = enroll(train_fnps)
    return r, c
