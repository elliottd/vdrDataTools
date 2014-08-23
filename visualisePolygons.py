from matplotlib import pyplot
from shapely.geometry import LineString
import sys
import getopt
from skimage.io import imread
from skimage.measure import regionprops, approximate_polygon
from subprocess import call

class VisualisePolygons:
  
  COLOR = {
    'a':  '#6699cc',
    'a2': '#ffcc33'
  }

  def rawdata(self, f):
    handle = open(f)
    data = handle.readlines()
    handle.close()
    return data

  def raw_polygons(self, data):
    polygons = []
    polygon = []
    for line in data:
        if line[1].isalpha():
            polygon.append(line[:-1])
            continue
        if len(line) == 0:
            continue
        else:
            line = line[:-2].split(" ")
            points = []
            for i in range(0, len(line), 2):
                points.append((int(line[i]), int(line[i+1])))
            polygon.append(points)
            polygons.append(polygon)
            polygon = []

    return polygons

  def area(self, pts):
    # Taken from http://paulbourke.net/geometry/polygonmesh/python.txt
    area=0
    nPts = len(pts)
    j=nPts-1
    i = 0
    for point in pts:
      p1=pts[i]
      p2=pts[j]
      area+= (p1[0]*p2[1])
      area-=p1[1]*p2[0]
      j=i
      i+=1

    area/=2;
    return area;

  def centroid(self, pts):
    # Taken from http://paulbourke.net/geometry/polygonmesh/python.txt
    nPts = len(pts)
    x=0
    y=0
    j=nPts-1;
    i = 0
    tpts = []
    for z in pts:
      a = []
      a.append(float(z[0]))
      a.append(float(z[1]))
      tpts.append(a)
    pts = tpts

    for point in pts:
      p1=pts[i]
      p2=pts[j]
      f=p1[0]*p2[1]-p2[0]*p1[1]
      x+=(p1[0]+p2[0])*f
      y+=(p1[1]+p2[1])*f
      j=i
      i+=1

    f=self.area(pts)*6
    return [x/f, y/f]

  def __init__(self, args):
    self.args = args

  def get_color(self, annotator):
    return self.COLOR[annotator]

  def plot_line(self, p1, p2, height, annotator):
    pyplot.plot([p2[0], p1[0]], [p2[1], p1[1]], color=self.get_color(annotator), alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)

  def get_width(self, image):
    return len(image[0])

  def get_height(self, image):
    return len(image)

  def draw_polygons(self, data, annotator, im):
    for polygon in data:      
      for p in polygon[1:]:
        i = 0
        for i in range(len(p)-1):
          self.plot_line(p[i], p[i+1], self.get_height(im), annotator)
          pyplot.annotate(polygon[0], xy=(p[0][0], p[1][1]), xytext=((p[0][0], p[1][1])), color="black", size='medium')
        c = self.centroid(p)
        pyplot.annotate("X", xy=(c[0], c[1]), color="#FFFFFF", size="medium")

  def run(self):
    i = self.args.get("-i")
    a = self.args.get("-a")

    im = imread(i)
    implot = pyplot.imshow(im, origin="upper")

    call(["python extractPolygons.py -i %s" % a], shell=True)

    a = a.replace(".xml",".polys")

    polygons = self.raw_polygons(self.rawdata(a))
    self.draw_polygons(polygons, 'a', im)

    #pyplot.axis([0, self.get_width(im), 0, self.get_height(im)])
    
    pyplot.show()

class Arguments:

  options = ["-i", "-a", "-h"] # -h is reserved.

  def options_string(self, options):
    # This function turns a list of options into the string format required by
    # getopt.getopt

    stringified = ""

    for opt in self.options:
      # We remove the first character since it is a dash
      stringified += opt[1:] + ":"

    return stringified

  def process_arguments(self, argv):
    # This function extracts the script arguments and returns them as a tuple.
    # It almost always has to be defined from scratch for each new file =/

    if (len(argv) == 0):
      self.usage()
      sys.exit(2)

    arguments = dict()
    stroptions = self.options_string(self.options)

    try:
      opts, args = getopt.getopt(argv, stroptions)
    except getopt.GetoptError:
      self.usage()
      sys.exit(2)

    # Process command line arguments
    for opt, arg in opts:
      if opt in ("-h"):      
        self.usage()                     
        sys.exit()
      for o in self.options:
        if opt in o:
          arguments[o] = arg
          continue

    return arguments

  def usage(self):
    # This function is used by process_arguments to echo the purpose and usage 
    # of this script to the user. It is called when the user explicitly
    # requests it or when no arguments are passed
    print("visualisePolygons overlays the polygons from a LabelMe annotation onto an image") 
    print("Usage: python visualisPolygons.py -i -a")
    print("-i, the name of the image file")
    print("-a, file with the LabelMe annotations")

def main(argv):

  # Get the arguments passed to the script by the user
  processor = Arguments()
  args = processor.process_arguments(argv)
  vp = VisualisePolygons(args)
  vp.run()

if __name__ == "__main__":
  main(sys.argv[1:])
