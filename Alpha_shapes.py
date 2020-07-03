import sys
import matplotlib.pyplot as plt
import alphashape
from shapely.geometry import Polygon

points = [(0., 0.), (0., 1.), (1., 1.), (1., 0.),
          (0.5, 0.25), (0.5, 0.75), (0.25, 0.5), (0.75, 0.5)]

alpha_shape = list(alphashape.alphashape(points, 2.0).exterior.coords.xy[0])

print(alpha_shape)
