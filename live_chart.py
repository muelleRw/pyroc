from op_180 import op_180
from pylive import live_plotter
import numpy as np

size = 300 #5 minutes * 300 ~ 24hrs
x_vec = np.linspace(0,1,size+1)[0:-1]
y_vec = np.random.randn(len(x_vec))
line1 = []

points = [[10, 0, 0], [10, 0, 1], [10, 0, 2]]
x = op_180("COM1", 9600)

while True:
    vals = x.poll(points, 300)#every 5 minutes
    y_vec[-1] = vals["Temperature"][0]
    line1 = live_plotter(x_vec, y_vec, line1)
    y_vec = np.append(y_vec[1:], 0.0)
