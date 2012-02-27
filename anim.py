import time
import pylab
# interactive mode on
pylab.ion()
timefig = pylab.figure(1)
timesub = pylab.subplot(111)
dt = 0.1
t = pylab.arange(0.0, 2.0, dt)
h = 1.2*pylab.sin(t)
lines = pylab.plot(t,h)
for i in range(8):
    t = t + dt
    h = 1.2*pylab.sin(t)
    lines[0].set_data(t,h)
    timesub.set_xlim((t[0],t[-1]))
    pylab.draw()
    time.sleep(1.0)
