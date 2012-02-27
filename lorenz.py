#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from enthought.mayavi import mlab

def lorenz(x, y, z, s=10., r = 28., b = 8./3. ):
    """Evaluate velocity"""
    u = s*(y-x)
    v = r*x - y - x*z
    w = x*y - b*z
    return u, v, w

x, y, z = numpy.mgrid[-50:50:100j, -50:50:100j, -10:60:70j]
u, v, w = lorenz(x,y,z)
f = mlab.flow(x,y,z,u,v,w)
o = mlab.outline()
mlab.show()

