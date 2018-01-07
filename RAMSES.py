import DTCurrentPlot
import DTCurrentData
import numpy as np
import matplotlib.pyplot as plt

data = DTCurrentData.DTCurrentData('Fills/2015/4485/')
data2 = DTCurrentData.DTCurrentData('Fills/2015/4440/')

#xs, ys = data.current_vs_PMIL5515(wheel=2, station=4, sector=4, superlayer=1)
#plt.plot(xs, ys, '.',c="r",label='PMIL5515')
#xs, ys = data.current_vs_PMIL5501(wheel=2, station=4, sector=4, superlayer=1)
#plt.plot(xs, ys, '.',c="g",label='PMIL5501')
#xs, ys = data.current_vs_PMIL5522(wheel=2, station=4, sector=4, superlayer=1)
#plt.plot(xs, ys, '.',c="m",label='PMIL5522')

#xs, ys = data.current_vs_PMIL5515(wheel=-1, station=4, sector=4,  )
#plt.plot(xs, ys, '.',c="r",label='PMIL5515 4440')

xs, ys = data.current_vs_PMIL5515(wheel=-1, station=4, sector=4,  superlayer=1)
plt.plot(xs, ys, '.',c="r",label='SL1 YB-1 S4 MB4 4485')

xs, ys = data2.current_vs_PMIL5515(wheel=-1, station=4, sector=4, superlayer=1 )
plt.plot(xs, ys, ',',c="r",label='SL1 YB-1 S4 MB4 4440')

xs, ys = data.current_vs_PMIL5515(wheel=-1, station=4, sector=4,  superlayer=2)
plt.plot(xs, ys, '.',c="b",label='SL2 YB-1 S4 MB4 4485')

xs, ys = data2.current_vs_PMIL5515(wheel=-1, station=4, sector=4, superlayer=2 )
plt.plot(xs, ys, ',',c="b",label='SL2 YB-1 S4 MB4 4440')

#xs, ys = data2.current_vs_PMIL5515(wheel=-1, station=4, sector=4,  )
#plt.plot(xs, ys, '.',c="r",label='Lumi 4485')
title = "Comparison Runs"
#plt.title(r'$\alpha > \beta$')
#plt.ylabel(r'$\mu$ A / ')
plt.xlabel(r'Ramses Measurement $\mu$ S/h')
#plt.ylabel(r'Ramses Measurement PMIL5514 $\mu$ S/h')
#plt.ylabel(r'Mean Current for wire channel $\mu$A')
#plt.xlabel('Luminosity')
plt.title(title)
#plt.plot(xs, ys, '.', c=colors[0], label='current')
plt.legend(loc='upper left', ncol=1, frameon=False, numpoints=1)
plt.grid()
plt.show()
#plt.savefig(self.path + filename, bbox_inches='tight')

