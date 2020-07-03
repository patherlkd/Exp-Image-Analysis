import matplotlib.pyplot as plt
import math
from random import uniform
from random import seed

# Returns the polar angle
def angle(p1,p2):
	ang = 0.0
	if p1[0] >= p2[0]:
		ang = math.pi - math.acos((p1[0]-p2[0])/math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2))
	else:
		ang = math.acos((p2[0]-p1[0])/math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2))

	return ang

# Returns the determinant of the 3x3 matrix...
# 	[p1(x) p1(y) 1]
#	[p2(x) p2(y) 1]
# 	[p3(x) p3(y) 1]
# If >0 then counter-clockwise
# If <0 then clockwise
# If =0 then collinear
def ccw(p1,p2,p3):
	return (p2[0]-p1[0])*(p3[1]-p1[1])-(p2[1]-p1[1])*(p3[0]-p1[0])

# returns the convex hull (boundary) using Graham's scan
def get_boundary(points):

    min_j = 10**7
    P0 = []

    # find the lowest j coordinate
    for pnt in points:
      if pnt[1] <= min_j:
        P0 = pnt
        min_j = pnt[1]

    # if there are two points with the same j then choose by i
    min_i = P0[0]

    P1 = []

    for pnt in points:
    	if pnt == P0:
    		continue
    	
    	if((pnt[1]<=min_j) and (pnt[0] < P0[0])):
    		P1 = pnt
    		min_i = pnt[0]
    	else:
    		P1 = P0

    # sort by polar angle

    pnts_n_angles = []

    for pnt in points:
    	if pnt == P1:
    		continue
    	else:
    		pnts_n_angles.append([pnt,angle(P1,pnt)])

   
    pnts_n_angles = sorted(pnts_n_angles, key=lambda x: x[1])
    
    points = [row[0] for row in pnts_n_angles]
    
    # traverse sorted points 
    
    S = [P1,points[0]]

    del points[0]

    for pnt in points:

    	while( len(S) >= 2) and (ccw(S[-2],S[-1],pnt) <= 0):

    		S.pop(-1)
    		
    	S.append(pnt)
    
    S.append(P1)
    return S
