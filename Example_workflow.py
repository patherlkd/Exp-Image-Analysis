import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import py_image_LD as ImLD
from PIL import Image
from PIL import ImageFilter
import time
import cluster

folder = "Folder/"

basename = 'images_' 
extension = '.tiff' # as an example

image_index_min = 3
image_index_max = 80

images = []
np_im_arrays = []

for i in range(image_index_min,image_index_max+1):
	image = Image.open(folder+basename+"{:04d}".format(i)+extension).convert('L')
	images.append(image.filter(ImageFilter.MedianFilter(size=9))) # apply a median filter
	images[-1].filter(ImageFilter.GaussianBlur(radius=4)) # apply a Gaussian blur
	np_im_arrays.append(np.array(image))

area_per_pixel = 4.0/(np_im_arrays[-1].shape[0]*np_im_arrays[-1].shape[1]) # units of micro metres squared

## show histogram for to get values of intensities to segment image

## use last image as this will give us most information

histoIn = ImLD.histogram_intensity(np_im_arrays[-1])
plt.figure(figsize=[10,8])
plt.bar(histoIn[1][:-1], histoIn[0], width = 0.5, color='#0504aa',alpha=0.7)
plt.xlabel('Color intensity values',fontsize=15)
plt.ylabel('Frequency',fontsize=15)
plt.show()


# 'thinned' and 'channels' are just example names of features in the images.

## write down the approx min and max intensity/color values for the objects

channelIn_min = ImLD.min_intensity(np_im_arrays[-1])
channelIn_max = 32

thinnedIn_min = 30
thinnedIn_max = 75

## check channels

channel_array = ImLD.grab_intensity_band(np_im_arrays[-1],channelIn_min,channelIn_max)

print("Final channel coverage: "+str(ImLD.total_surface_coverage(channel_array)))

test_image = Image.fromarray(channel_array)

test_image.show()

## check thinned

thinned_array = ImLD.grab_intensity_band(np_im_arrays[-1],thinnedIn_min,thinnedIn_max)

print("Final Thinned coverage: "+str(ImLD.total_surface_coverage(thinned_array)))

test_image = Image.fromarray(thinned_array)

test_image.show()

## # for saving channels images

print("Saving feature images in folder: "+folder)

cnt = image_index_min

for np_array in np_im_arrays:
	channel_array = ImLD.grab_intensity_band(np_array,channelIn_min,channelIn_max)
	thinned_array = ImLD.grab_intensity_band(np_array,thinnedIn_min,thinnedIn_max)
	chanimage = Image.fromarray(channel_array).convert('RGB')
	thinimage = Image.fromarray(thinned_array).convert('RGB')
	chanimage.save(folder+"channels_"+basename+"{:04d}".format(cnt)+'.png')
	thinimage.save(folder+"thinned_"+basename+"{:04d}".format(cnt)+'.png')
	cnt+=1

print("Done.")

## Analysing total coverage of the features

frames = range(len(np_im_arrays))

## clustering -> no. of thinned and channels against time

channel_numbers = []
thinned_numbers = []

chan_trajectories = []
thin_trajectories = []

frame = 0

start_time = time.time()

for np_array in np_im_arrays:
	print("Frame: "+str(frame))

	channel_array = ImLD.grab_intensity_band(np_array,channelIn_min,channelIn_max)
	thinned_array = ImLD.grab_intensity_band(np_array,thinnedIn_min,thinnedIn_max)

	chan_clusters = cluster.clusterize_array(channel_array,neigh_ratio_crit=0.7)
	thin_clusters = cluster.clusterize_array(thinned_array,neigh_ratio_crit=0.3)

	chan_clusters = cluster.select_clusters_by_size(chan_clusters,25)
	#channel_numbers.append(len(chan_clusters))

	thin_clusters = cluster.select_clusters_by_size(thin_clusters,100)
	#thinned_numbers.append(len(thin_clusters))

	for chan_clust in chan_clusters:
		added_to_traj = False

		for chan_traj in chan_trajectories: # attempt to add to existing trajectories
			added_to_traj = chan_traj.add_to_trajectory(chan_clust)
			if(added_to_traj):
				break

		if(not added_to_traj):
			chan_trajectories.append(cluster.cluster_trajectory(chan_clust,frame))

	for thin_clust in thin_clusters:
		added_to_traj = False

		for thin_traj in thin_trajectories: # attempt to add to existing trajectories
			added_to_traj = thin_traj.add_to_trajectory(thin_clust)
			if(added_to_traj):
				break

		if(not added_to_traj):
			thin_trajectories.append(cluster.cluster_trajectory(thin_clust,frame))


	frame += 1

end_time = time.time()

print("Clustering took this many seconds: "+str(end_time-start_time))

print("Saving the cluster files")

thin_clust_dir = 'thinned_cluster_trajs/'
chan_clust_dir = 'channel_cluster_trajs/'

try:
	os.mkdir(folder+thin_clust_dir)
except OSError as error:
		pass

try:
	os.mkdir(folder+chan_clust_dir)
except OSError as error:
		pass

cnt = 1
for thin_traj in thin_trajectories:
	savedir = folder+thin_clust_dir+'traj_'+str(cnt)+'/'
	try:
		os.mkdir(savedir)
	except OSError as error:
		pass

	thin_traj.save_trajectory(savedir,np_im_arrays[-1].shape[1])
	#thin_traj.animate(np_im_arrays[-1].shape[1])
	#chan_traj.animate_boundary(np_im_arrays[-1].shape[1])
	cnt += 1

cnt = 1
for chan_traj in chan_trajectories:
	savedir = folder+chan_clust_dir+'traj_'+str(cnt)+'/'
	try:
		os.mkdir(savedir)
	except OSError as error:
		pass

	chan_traj.save_trajectory(savedir,np_im_arrays[-1].shape[1])
	#thin_traj.animate(np_im_arrays[-1].shape[1])
	#chan_traj.animate_boundary(np_im_arrays[-1].shape[1])
	cnt += 1

print("Done.")

