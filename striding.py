# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 21:47:06 2017

@author: jussi
"""


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
     
