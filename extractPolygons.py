import getopt
import sys
import os
from xml.dom import minidom

def parse_xml(file):
    dom = minidom.parse(file)
    objects = dom.getElementsByTagName("object")
    data = []

    for idx,o in enumerate(objects):
        odata = []
        label = str(o.getElementsByTagName("name")[0].childNodes[0].data)
        odata.append(label)
        xmlpoints = o.getElementsByTagName("pt")
        for idx, point in enumerate(xmlpoints):
            xval = str(point.getElementsByTagName("x")[0].childNodes[0].data)
            yval = str(point.getElementsByTagName("y")[0].childNodes[0].data)
            odata.append([xval, yval])
        data.append(odata)

    return data

def usage():
    print("extractPolygons extracts the labelled polygons from a LabelMe XML file")
    print("The extracted polygons are written to the same directory as the input file")
    print("Usage: python extractPolygons.py -i {input file}")
    print("-i, the LabelMe XML file")

def process_arguments(argv):
    if (len(argv) == 0):
        usage()
        sys.exit(2)
    
    inputfile = None

    try:
        opts, args = getopt.getopt(argv, "hi:", ["help", "inputfile="])
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

    return (inputfile)

def write_parsed(file, data):
    file = file.replace(".xml", ".polys")
    output = open(file, "w")
    for object in data:
        yvals = []
        first = []
        for idx, i in enumerate(object):
            if idx == 0:
                output.write(object[0] + "\n")
                continue
            if idx == 1:
                first.append(i[0])
                first.append(i[1])
            output.write("%s %s " %(i[0], i[1]))
            if idx == len(object)-1:
                output.write("%s %s " % (first[0], first[1]))
            yvals.append(i[1])
        output.write("\n")
    output.close()

def main(argv):
    inputfile = process_arguments(argv)
    parsed = parse_xml(inputfile)
    write_parsed(inputfile, parsed)

if __name__ == "__main__":
    main(sys.argv[1:])
