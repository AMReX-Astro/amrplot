# running with ipython --matplotlib=qt works

import matplotlib
matplotlib.use("QT4Agg")
import matplotlib.pyplot as plt
#plt.ion()

print(plt.get_backend())

import yt
yt.toggle_interactivity()


ds = yt.load("sedov_2d_sph_in_cyl_plt00000")

slc = yt.SlicePlot(ds, "z", "density")
plt.pause(0.001)
slc.show()

a = input("press a key")


