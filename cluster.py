import alphashape
import numpy as np
import matplotlib.pyplot as plt

def iterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True

def select_boundaries_by_size(boundaries,N):
  new_boundaries = []

  for boun in boundaries:
    if len(boundaries) > N:
      new_boundaries.append(boun)
  return new_boundaries

def select_clusters_by_size(clusters,N,Nbig=10**3):
  new_clusters = []

  for clust in clusters:
    if (clust.size() > N) and (clust.size() < Nbig):
      new_clusters.append(clust)

  return new_clusters

def upload_snakes(filename,ysize):

  trajectories = []

  with open(filename,'r') as file:

    lncnt = 1
    Ntraj = 1
    traj = None
    clust_ids = []
    clust = None
    for line in file:
      if lncnt <= 9: # skip first 9 lines of file
        lncnt += 1
        continue

      parts = line.split()

      if parts[0] == '#':

        if traj is not None:
          trajectories.append(cluster_trajectory(traj,min(clust_ids),Ntraj))

        traj = []
        Ntraj += 1
        clust_ids = []
        clust = None
      elif parts[0] == '1':
        continue
      else:
        if int(parts[1]) == 0:

          if clust is not None:
            traj.append(clust)

          clust_ids.append(int(parts[0]))
          clust = cluster(int(parts[0]))
          clust.add_to_cluster([int(float(parts[2])),ysize-int(float(parts[3]))])
        else:
          clust.add_to_cluster([int(float(parts[2])),ysize-int(float(parts[3]))])


  return trajectories

class cluster_trajectory:
  def __init__(self,clust,start_frame,traj_id=0):
    self.traj_id = traj_id
    self.start_frame = start_frame
    self.clusters = [clust]
    self.info = []

    if iterable(self.clusters[0]):
      self.clusters = self.clusters[0]

  def get_info(self,index):
    if index >= len(self.info):
      return None
    else:
      return self.info[index]

  def display_info(self):
    print(self.info)

  def add_to_info(self,item):
    self.info.append(item)

  def set_end_frame(self,end_frame):
    self.end_frame = end_frame

  def save_trajectory(self,savedir,ysize):
    frame = self.start_frame
    for clust in self.clusters:
      filename = 'frame_'+str(frame)+'.txt'
      with open(savedir+filename,'w') as output:
        output.write(clust.get_points_for_file(ysize))
      frame +=1

  def sort_by_id(self,rev=True):
    self.clusters = sorted(self.clusters,key=lambda clust: clust.get_id(),reverse=rev)

  def id_match(self,traj_id):
    if self.traj_id == traj_id:
      return True
    else:
      return False

  def get_id(self):
    return self.traj_id

  def get_cluster_with_id(self,c_id):
    for clust in self.clusters:
      if clust.check_id(c_id):
        return clust
    return None

  def get_cluster_ids(self):
    ids = []
    for clust in self.clusters:
      ids.append(clust.get_id())
    return ids

  def get_cluster_centroids(self):
    centroids = []
    for clust in self.clusters:
      centroids.append(clust.get_centroid())
    return centroids

  def get_cluster_sizes(self):
    sizes = []
    for clust in self.clusters:
      sizes.append(clust.get_size())

  def get_size(self):
    return len(self.clusters)

  def get_start_frame(self):
    return self.start_frame

  def add_to_trajectory(self,clust):
    success = False

    c1 = self.clusters[-1].get_centroid()
    c2 = clust.get_centroid()

    dr2 = (c1[0]-c2[0])**2 + (c1[1]-c2[1])**2

    # check if they have at least one point in common

    point_check = False

    for c1_point in self.clusters[-1].get_points():
      for c2_point in clust.get_points():
        if c1_point == c2_point:
          point_check = True
          break

    if (dr2<=16.0) and (point_check):
      self.clusters.append(clust)
      success=True
    return success

  def animate_concave_boundary(self):
    for clust in self.clusters:
      coords = np.array(clust.get_concave_boundary(1.0))
      
      x = coords[:,0]

      #correct y coordinate (reflect)
      y = coords[:,1]
      plt.plot(x,y,'s')
      plt.plot(x,y)
    #plt.show()

  def animate(self,ysize):
    for clust in reversed(self.clusters):
      coords = np.array(clust.get_points())
      
      x = coords[:,1]

      #correct y coordinate (reflect)
      y = [ysize-i for i in coords[:,0]]
      plt.plot(x,y,'s')
   # plt.show()

  def animate_raw(self):
    for clust in reversed(self.clusters):
      coords = np.array(clust.get_points())
      
      x = coords[:,0]
      y = coords[:,1]
      plt.plot(x,y,'s')
    #plt.show()

  def animate_centroids_raw(self,col='blue'):
    x = []
    y = []
    for clust in reversed(self.clusters):
      cent = clust.get_centroid()
      x.append(cent[0])
      y.append(cent[1])
    plt.plot(x,y,color=col)
    #plt.show()



class cluster:
  def __init__(self,c_id,startpoint=[0,0]):
    self.points = [startpoint]
    self.concave_boundary = []
    self.convex_boundary = []
    if startpoint == [0,0]:
      self.points = []
    self.id = c_id

  def size(self):
    return len(self.points)

  def get_centroid(self):
    meani = 0.0
    meanj = 0.0

    for pnt in self.points:
      meani += pnt[0]
      meanj += pnt[1]

    meani = meani/self.size()
    meanj = meanj/self.size()

    return [meani,meanj]

  def min_boundary_distance(self,clust):
    b1 = self.get_concave_boundary(1.0)
    b2 = clust.get_concave_boundary(1.0)

    min_dr2 = 10**7

    for pnt1 in b1:
      for pnt2 in b2:
        dr2 = (pnt1[0]-pnt2[0])**2 + (pnt1[1]-pnt2[1])**2

        if dr2 < min_dr2:
          min_dr2 = dr2

    return min_dr2

  def get_convex_boundary(self): # uses Graham's scan: convex hull algorithm
    if len(self.convex_boundary) > 0:
      return self.convex_boundary
    else:
      self.convex_boundary = gs.get_boundary(self.points)
      return self.convex_boundary
  
  def get_concave_boundary(self,alpha):
    if alpha == 0:
      return self.get_convex_boundary()
    elif (alpha > 0) and (alpha <= 2):
      if len(self.concave_boundary) > 0:
        return self.concave_boundary

      polygon = alphashape.alphashape(self.points, alpha)

      if not iterable(polygon):
        x = list(polygon.exterior.coords.xy[0])
        y = list(polygon.exterior.coords.xy[1])
        return list(zip(x,y))
      else:
        xlist = []
        ylist = []
        for poly in polygon:
          xlist.append(list(poly.exterior.coords.xy[0]))
          ylist.append(list(poly.exterior.coords.xy[1]))
        
        x = []

        for sl in xlist:
          for item in sl:
            x.append(item)

        y = []
        
        for sl in ylist:
          for item in sl:
            y.append(item)

        self.concave_boundary = list(zip(x,y))
        return self.concave_boundary

    else:
      print("Alpha variable < 0 or > 2")
      return None

  def absorb_cluster(self,c):
    for pnt in c.get_points():
      self.add_to_cluster(pnt)

  def is_empty(self):
    if len(self.points) == 0:
      return True
    else:
      return False

  def get_points(self):
    return self.points

  def plot_concave_boundary(self,ysize):
    x = []
    y = []
    for pnt in self.get_concave_boundary(1.0):
      x.append(pnt[1])
      y.append(ysize-pnt[0])
    plt.plot(x,y,'o')

  def plot_cluster(self,col='blue',lines=False):
    x = []
    y = []
    for pnt in self.points:
      x.append(pnt[0])
      y.append(pnt[1])
    if not lines:
      plt.plot(x,y,'o',color=col)
    else:
      plt.plot(x,y,color=col)

  def get_points_for_file(self,ysize):
    points_string = ''
    for pnt in self.points:
      points_string += str(pnt[1])+"\t"+str(ysize-pnt[0])+"\n"

    return points_string

  def set_id(self,c_id):
    self.id = c_id

  def get_id(self):
    return self.id

  def check_id(self,c_id):
    if self.id == c_id:
      return True
    else:
      return False

  def clear_cluster(self):
    self.points = []

  def add_to_cluster(self,point):
    self.points.append(point)

  def check_in_cluster(self,point):
    for pnt in self.points:
      if pnt == point:
        return True
    return False

def clusterize_array(np_array,avoid=255,neigh_ratio_crit=0.5):
  xsize = np_array.shape[0]
  ysize = np_array.shape[1]

  clusters = []

  clust_id = 0

  print("Clusterizing...")

  for i in range(0,xsize,2):
    #print("N Clusters: "+str(len(clusters))+" at i ="+str(i)) 
    for j in range(0,ysize,2):
      if np_array[i,j] == avoid:
        continue
      else:

        neighs = []

        # add allowable neighbors

        avoid_cnt = 0

        for neighi in [i-1,i+1]:
          if neighi >= 0 and neighi < xsize:
            neighs.append([neighi,j])
            if np_array[neighi,j] == avoid:
              avoid_cnt += 1
        for neighj in [j-1,j+1]:
          if neighj >= 0 and neighj < ysize:
            neighs.append([i,neighj])
            if np_array[i,neighj] == avoid:
              avoid_cnt += 1
            for neighi in [i-1,i+1]:
              if neighi >= 0 and neighi < xsize:
                neighs.append([neighi,neighj])
                if np_array[neighi,neighj] == avoid:
                  avoid_cnt += 1

        if avoid_cnt/len(neighs) > neigh_ratio_crit:
          continue
        else:
          for neigh in neighs:
            if np_array[neigh[0],neigh[1]] == avoid:
              continue
            else:
              if len(clusters) == 0:
                clust_id += 1
                clust = cluster(clust_id,[i,j])
                clust.add_to_cluster(neigh)
                clusters.append(clust)
                
              else:

                clust1 = 0
                clust1index = 0
                clust2 = 0
                clust2index = 0

                point1_in_clust = False
                point2_in_clust = False

                index = 0

                for clust in clusters:

                  if clust.check_in_cluster([i,j]):
                    point1_in_clust = True
                    clust1 = clust
                    clust1index = index

                  if clust.check_in_cluster(neigh):
                    point2_in_clust = True
                    clust2 = clust
                    clust2index = index
                  index += 1

                if((point1_in_clust) and (not point2_in_clust)):
                  clust1.add_to_cluster(neigh)
                elif((not point1_in_clust) and (point2_in_clust)):
                  clust2.add_to_cluster([i,j])
                elif((point1_in_clust) and (point2_in_clust)):
                  if clust1.get_id()==clust2.get_id():
                    pass
                  else:
                    clust1.absorb_cluster(clust2)
                    clust2.clear_cluster()
                    clusters.pop(clust2index) # clean the clusters list
                    
                elif((not point1_in_clust) and (not point2_in_clust)):
                  clust_id += 1
                  newclust = cluster(clust_id,[i,j])
                  newclust.add_to_cluster(neigh)
                  clusters.append(newclust)

  print("Done.")
  return clusters

