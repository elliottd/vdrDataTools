import getopt
import sys
import os
from xml.dom import minidom
import re
  
def write_dot(data, filename, outputdir, number):
    filename = filename.replace(".xml", "")
    filename = filename.split("/")
    for idx,p in enumerate(filename):
        if p.startswith("20"):
            filename = filename[idx]
            break
    output = open(str.format("%s/%s-%d.dot" % (outputdir, filename, number)), "w")
    output.write('digraph "g" {' + "\n")
    for objidx, obj in enumerate(data):
        print obj
        for idx, i in enumerate(obj):
            if idx == 0:
                output.write(str.format('"n%d" [\n label="%s" \n comment="(%.3f, %.3f)" \n]' % (objidx+1, obj[0], obj[1][0], obj[1][1])))
                continue
            if idx == 1:
                continue
        output.write("\n")
    output.write(str.format('"n%d" [label=ROOT] \n' % (0)))    
    output.write("}")
    output.close()

def area(pts):
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

def centroid(pts):
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

    f=area(pts)*6
    return [x/f, y/f]

def parse_xml(filename):
    dom = minidom.parse(filename)
    objects = dom.getElementsByTagName("object")
    data = []

    for idx,o in enumerate(objects):
        odata = []
        label = str(o.getElementsByTagName("name")[0].childNodes[0].data)
        odata.append(label)
        td = []
        xmlpoints = o.getElementsByTagName("pt")
        for idx, point in enumerate(xmlpoints):
            xval = str(point.getElementsByTagName("x")[0].childNodes[0].data)
            yval = str(point.getElementsByTagName("y")[0].childNodes[0].data)
            td.append([xval, yval])
        c = centroid(td)
        odata.append(c)
        odata.append(td)
        data.append(odata)

    # Sort the data so it is in alphabetical order to minimise tree mismatches

    data.sort()

    return data

def usage():
    print("xml2dot converts an XML file from LabelMe into three .dot files")
    print("Usage: python xml2dot.py -i {input file} -o {output directory}")
    print("-i, the XML file to convert")
    print("-o, the directory to write the DOT files (default=dotfiles)")

def process_arguments(argv):
    if (len(argv) == 0):
        usage()
        sys.exit(2)
    
    inputfile = None
    outputdir = "dotfiles"

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["help", "inputfile=", "outputdir="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    # Process command line arguments
    for opt, arg in opts:
        if opt in ("-h", "--help"):      
            usage()                     
            sys.exit()
        elif opt in ("-i", "--inputfile"):
            inputfile = arg
        elif opt in ("-o", "--outputdir"):
            outputdir = arg

    return (inputfile, outputdir)

def main(argv):
    (inputfile, outputdir) = process_arguments(argv)
    parsed = parse_xml(inputfile)
    write_dot(parsed, inputfile, outputdir, 1)
    write_dot(parsed, inputfile, outputdir, 2)
    write_dot(parsed, inputfile, outputdir, 3)

if __name__ == "__main__":
    main(sys.argv[1:])
