"""
06 Aug 2013


"""

from bisect    import bisect_left
from itertools import combinations
from math      import log10
import numpy as np


class Interpolate(object):
    """
    simple linear interpolation
    """
    def __init__(self, x_list, y_list):
        for i, (x, y) in enumerate(zip(x_list, x_list[1:])):
            if y - x < 0:
                raise ValueError("x must be in strictly ascending")
            if y - x == 0 and i >= len(x_list)-2:
                x_list = x_list[:-1]
                y_list = y_list[:-1]
        if any(y - x <= 0 for x, y in zip(x_list, x_list[1:])):
            raise ValueError("x must be in strictly ascending")
        x_list = self.x_list = map(float, x_list)
        y_list = self.y_list = map(float, y_list)
        intervals = zip(x_list, x_list[1:], y_list, y_list[1:])
        self.slopes = [(y2 - y1)/(x2 - x1) for x1, x2, y1, y2 in intervals]
        
    def __call__(self, x):
        i = bisect_left(self.x_list, x) - 1
        return self.y_list[i] + self.slopes[i] * (x - self.x_list[i])


def zscore(values, size):
    """
    _______________________/___
                          /
                         /
                        /
                       /
                      /
                     /
                    /
                   /
                  /
                 /
                /
               /
              /                     score
          ___/_________________________________
            /

    """
    # do not take into account the diagonal
    nop = dict([(i + size * i,  None) for i in xrange(size)])
    # Set the virtual minimum of the matrix to half the non-null real minimum
    minv = min([v for v in values if v]) / 2
    if minv > 1:
        minv /= 2
    # get the log10 of values
    vals = [log10(v) if v > 0 and not v in nop else log10(minv) for v in values]
    mean_v = np.mean(vals)
    std_v  = np.std(vals)
    # replace values by z-score
    for i in xrange(len(values)):
        if values[i] > 0:
            values[i] = (vals[i] - mean_v) / std_v
        elif values[i] == 0:
            values[i] = (log10(minv) - mean_v) / std_v
        else:
            values[i] = -99


def calinski_harabasz(scores, clusters):
    """
    Implementation of the CH score [CalinskiHarabasz1974]_, that has shown to be
    one the most accurate way to compare clustering methods
    [MilliganCooper1985]_ [Tibshirani2001]_.

    The CH score is:

    .. math::

        CH(k) = \\frac{B(k) / (k-1)}{W(k)/(n - k)}

    Where :math:`B(k)` and :math:`W(k)` are the between and within cluster sums
    of squares, with :math:`k` clusters, and :math:`n` the total number of
    elements (models in this case).
   
    :param scores: a dict with, as keys, a tuple with a pair of models; and, as
       value, the distance between these models.
    :param clusters: a dict with, as key, the cluster number, and as value a
       list of models
    :param nmodels: total number of models

    :returns: the CH score
    """
    cluster_list = [c for c in clusters if len(clusters[c]) > 1]
    if len(cluster_list) <= 1:
        return 0.0
    nmodels = sum([len(clusters[c]) for c in cluster_list])

    between_cluster = (sum([sum([sum([scores[(md1, md2)]**2
                                      for md1 in clusters[cl1]])
                                 for md2 in clusters[cl2]])
                            / (len(clusters[cl1]) * len(clusters[cl2]))
                            for cl1, cl2 in combinations(cluster_list, 2)])
                       / ((len(cluster_list) - 1.0) / 2))
    
    within_cluster = (sum([sum([scores[(md1, md2)]**2
                                for md1, md2 in combinations(clusters[cls], 2)])
                           / (len(clusters[cls]) * (len(clusters[cls]) - 1.0) / 2)
                           for cls in cluster_list]))
    
    return ((between_cluster / (len(cluster_list) - 1))
            /
            (within_cluster / (nmodels - len(cluster_list))))
