from PIL import Image
import sys
import numpy as np
import matplotlib.pyplot as plt
import Grahams_scan as gs
import alphashape
import cluster

def normalize_array(np_array):
  xsize = np_array.shape[0]
  ysize = np_array.shape[1]

  maxVal = -10**8

  for i in range(xsize):
    for j in range(ysize):
      if np_array[i,j] > maxVal:
        maxVal = np_array[i,j]

  new_array = np.zeros((xsize,ysize))

  for i in range(xsize):
    for j in range(ysize):
      new_array[i,j] =  np_array[i,j]/maxVal

  return new_array

def ave_intensity(np_array):
  xsize = np_array.shape[0]
  ysize = np_array.shape[1]

  ave = 0

  for i in range(xsize):
    for j in range(ysize):
      ave += np_array[i,j]

  ave = ave/(xsize*ysize)

  return int(ave)

def max_intensity(np_array):
  xsize = np_array.shape[0]
  ysize = np_array.shape[1]

  maxVal = -10**8

  for i in range(xsize):
    for j in range(ysize):
      if np_array[i,j] > maxVal:
        maxVal = np_array[i,j]

  return maxVal

def min_intensity(np_array):
  xsize = np_array.shape[0]
  ysize = np_array.shape[1]

  minVal = 10**8

  for i in range(xsize):
    for j in range(ysize):
      if np_array[i,j] < minVal:
        minVal = np_array[i,j]

  return minVal

def histogram_intensity(np_array):
  xsize = np_array.shape[0]
  ysize = np_array.shape[1]

  dat = []

  for i in range(xsize):
    for j in range(ysize):
      dat.append(np_array[i,j])

  hist = np.histogram(dat,bins=range(0,255))

  return hist
 
def grab_intensity_band(np_array,Min,Max):
  xsize = np_array.shape[0]
  ysize = np_array.shape[1]

  new_array = np.zeros((xsize,ysize))

  for i in range(xsize):
    for j in range(ysize):
      if np_array[i,j] >= Min and np_array[i,j] < Max:
        new_array[i,j] = np_array[i,j]
      else:
        new_array[i,j] = 255

  return new_array


def total_surface_coverage(np_array,avoid=255):
  xsize = np_array.shape[0]
  ysize = np_array.shape[1]

  totpixels = xsize*ysize

  pixelcnt = 0
  for i in range(xsize):
    for j in range(ysize):
      if not (np_array[i,j] == 255):
        pixelcnt+=1

  return pixelcnt/totpixels




              

    