import numpy as np

from src.filters import minucias


def _get_core(minutae: np.array):
    return [point for point in minutae if point[2] == minucias.MnType.Core][0]


def _extract_radial(minutae: np.array,
                    bucketsize: int):
    core = _get_core(minutae)
    if core is None:
        raise Exception('missing core point for polar method')

    feat = []
    for i in range(0, 360//bucketsize):
        feat.append({minucias.MnType.Termination: 0,
                     minucias.MnType.Bifurcation: 0})
    for point in minutae:
        i, j, t, _ = point if len(point) == 4 else point + (None,)
        if (t == minucias.MnType.Termination or t == minucias.MnType.Bifurcation) \
                and not (i == core[0] and j == core[1]):
            h = float(abs(i - core[0]))
            w = float(abs(j - core[1]))

            angle = None
            if i < core[0]:
                if j > core[1]:  # 1st quarter
                    angle = int(np.rad2deg(np.arctan(h/w)))
                elif j < core[1]:  # 2nd quarter
                    angle = int(np.rad2deg(np.arctan(w/h))) + 90
                else:
                    angle = 90
            elif i > core[0]:
                if j < core[1]:  # 3rd quarter
                    angle = int(np.rad2deg(np.arctan(h/w))) + 180
                elif j > core[1]:  # 4th quarter
                    angle = int(np.rad2deg(np.arctan(w/h))) + 270
                else:
                    angle = 270
            else:
                angle = 0 if j > core[1] else 180

            feat[angle//bucketsize][t] += 1

    return np.array(feat)


def _extract_circular(minutae: np.array,
                      bucketsize: int):
    core = _get_core(minutae)
    if core is None:
        raise Exception('missing core point for circular method')

    dist = []
    for point in minutae:
        i, j, t, _ = point if len(point) == 4 else point + (None,)
        dist.append(np.linalg.norm(
            np.array((core[0], core[1])) - np.array((i, j))))

    feat = []
    for i in range(0, int(np.max(dist))//bucketsize + 1):
        feat.append({minucias.MnType.Termination: 0,
                     minucias.MnType.Bifurcation: 0})
    for i in range(0, len(dist)):
        t = minutae[i][2]
        if t == minucias.MnType.Termination or t == minucias.MnType.Bifurcation:
            feat[int(dist[i])//bucketsize][t] += 1

    return np.array(feat)


def extract(minutae: np.array,
            method: str = None,
            bucketsize: int = None):
    if method == 'radial':
        return (_extract_radial(minutae, bucketsize), method)
    elif method == 'circular':
        if bucketsize is None:
            raise Exception('bucketsize must be provided for circular method')
        return (_extract_circular(minutae, bucketsize), method)
    else:
        raise Exception(method + ' is not supported')
