import os
import re
import sys
import getopt
import subprocess
import dot2conll as dotconverter

options = ["-p", "-h", "-a"] # -h is reserved.
stanford = "stanford-postagger-2012-01-06"
malt = "maltparser-1.7.2"

def concatenate_other(path, extension, output_file):
    '''
    Concatenate a collection of files with a given extension into
    the output_file.
    '''
    print("cat %s/*.%s ..." % (path, extension))
    os.system("cat %s/*.%s > %s" % (path, extension, output_file))
    print("... done.")    
    print
    
def dot_to_conll(dotfiles_dir):
    '''
    Converts the dot files to CoNLL format
    '''
    
    files = sorted(os.listdir(dotfiles_dir))
    for file in files:
        dc = dotconverter.DotConverter()
        parsed = dc.parse_dot(dotfiles_dir+"/"+file)
        dc.write_conll(parsed, dotfiles_dir+"/"+file)

def dot_to_labels(dotfiles_dir):
    '''
    Converts the dot files to a list of strings
    '''
    
    files = os.listdir(dotfiles_dir)
    files = sorted([x for x in files if x.endswith(".dot")])
    for file in files:
        dc = dotconverter.DotConverter()
        parsed = dc.parse_dot(dotfiles_dir+"/"+file)
        dc.write_txt(parsed[0], dotfiles_dir+"/"+file)

def dot_to_gold(dotfiles_dir):
    '''
    Converts the dot files to gold standard dependency parses
    '''
    
    files = os.listdir(dotfiles_dir)
    files = sorted([x for x in files if x.endswith(".dot")])
    fh = open("failures", "w")
    for file in files:
        try:
          dc = dotconverter.DotConverter()
          parsed = dc.parse_dot(dotfiles_dir+"/"+file)
          dc.write_gold(parsed[0], dotfiles_dir+"/"+file)
        except KeyError:
          fh.write(file+"\n")

def main(argv):

    # Get the arguments passed to the script by the user
    args = process_arguments(argv)

    dir = args['-p']

    print("Processing data in %s" % dir)

    ''' 
    Process the linguistic data.
    We need to cat everything to make the tagger and parser fast.
    (If we try to tag and parse each description separately then we
    are wasting time loading and unloading the trained models in memory.)
    Then we need to unpack the tagged and parsed representations into
    individual files. 
    '''
    
    text_dir = dir + "/textfiles"
    dotfiles_dir = dir + "/dotfiles"

    # Process the image data
    print("### Converting DOT to CoNLL format ###")
    dot_to_conll(dotfiles_dir)
    concatenate_other(dotfiles_dir, "conll", dir+"/target-parsed")
    print("### Converting DOT to labels ###")
    dot_to_labels(dotfiles_dir)
    concatenate_other(dotfiles_dir, "labs", dir+"/target-strings")
    print("### Converting DOT to gold undirected ###")
    dot_to_gold(dotfiles_dir)
    concatenate_other(dotfiles_dir, "gold", dir+"/target-GOLD")
       
def usage():
    # This function is used by process_arguments to echo the purpose and usage 
    # of this script to the user. It is called when the user explicitly
    # requests it or when no arguments are passed

    print
    print("processData takes the original data and performs the") 
    print("transformations required to make it compatible with the models")
    print("The transformed data is written to the same directories as the")
    print("original data")
    print("Usage: python processData.py -p {path to original data}")
    print

def options_string(options):
    # This function turns a list of options into the string format required by
    # getopt.getopt

    stringified = ""

    for opt in options:
        # We remove the first character since it is a dash
        stringified += opt[1:] + ":"

    return stringified

def process_arguments(argv):
    # This function extracts the script arguments and returns them as a tuple.
    # It almost always has to be defined from scratch for each new file =/

    if (len(argv) == 0):
        usage()
        sys.exit(2)

    arguments = dict()
    stroptions = options_string(options)

    try:
        opts, args = getopt.getopt(argv, stroptions)
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    # Process command line arguments
    for opt, arg in opts:
        if opt in ("-h"):      
            usage()                     
            sys.exit()
        for o in options:
            if opt in o:
                arguments[o] = arg
                continue

    return arguments

if __name__ == "__main__":
    main(sys.argv[1:])
