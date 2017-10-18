import yt
from yt.units import cm

ds = yt.load("plt06677")

print(ds.domain_left_edge)
print(ds.domain_right_edge)

xctr = 0.5*(ds.domain_left_edge[0] + ds.domain_right_edge[0])
yctr = 5000*cm

xwidth = ds.domain_right_edge[0] - ds.domain_left_edge[0]
ywidth = 1.e4*cm

print(yctr - 0.5*ywidth, yctr + 0.5*ywidth)

#slc = yt.SlicePlot(ds, "theta", "temperature", origin="native",
#                   center=(xctr,yctr,0.0), width=(xwidth,ywidth))

slc = yt.plot_2d(ds, "temperature", origin="native",
                   center=(xctr,yctr), width=(xwidth,ywidth))

slc.save("test.png")

