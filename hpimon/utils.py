# -*- coding: utf-8 -*-
"""
Misc utility functions for hpimon

@author: jussi (jnu@iki.fi)

"""

import numpy as np
from numpy.lib.stride_tricks import as_strided


def rolling_var_strided(m, fun, win, axis=None):
    """ Window array along axis with window length win. Apply fun to the
    windowed data and return result. """
    if axis is None:
        m = m.flatten()
        axis = 0
    sh = m.shape
    st = m.strides
    # break up the given dim into windows, insert a new dim
    sh_ = sh[:axis] + (sh[axis] - win + 1, win) + sh[axis+1:]
    # insert a stride for the new dim, same as for the given dim
    st_ = st[:axis] + (st[axis], st[axis]) + st[axis+1:]
    # apply fun on the new dimension
    # ms = as_strided(m, sh_, st_)
    return fun(as_strided(m, sh_, st_), axis=axis+1)


def running_sum(M, win, axis=None):
    """ Running (windowed) sum of sequence M using cumulative sum, along
    given axis. Extended from
    http://arogozhnikov.github.io/2015/09/30/NumpyTipsAndTricks2.html """
    if axis is None:
        M = M.flatten()
    s = np.cumsum(M, axis=axis)
    s = np.insert(s, 0, [0], axis=axis)
    len = s.shape[0] if axis is None else s.shape[axis]
    return (s.take(np.arange(win, len), axis=axis) -
            s.take(np.arange(0, len-win), axis=axis))


def running_var(M, win, axis=None):
    """ Running variance using running_sum.
    This is really fast but accuracy may be bad """
    w = float(win)
    M = M.astype(np.float64)  # ensure 64-bit for more accuracy
    m = running_sum(M, win, axis)/w
    m2 = running_sum(M**2, win, axis)/w
    return m2-m**2
