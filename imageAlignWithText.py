import os
import re
import sys
import getopt
import subprocess
import detect_alignments as alignmentdetector

options = ["-p", "-h", "-a"] # -h is reserved.
stanford = "stanford-postagger-2012-01-06"
malt = "maltparser-1.7.2"

def detect_alignments(type, source, target, basedir):
    '''
    Determines the alignments between the source and target strings.
    Writes the output to a file called alignments.
    '''
    
    ad = alignmentdetector.AlignmentDetector()
    if type == "lexical":
        alignments = ad.lexical_alignments(source, target, basedir+"clusters")
    if type == "wordnet":
        alignments = ad.wordnet_alignments(source, target)

    ad.write_alignments(alignments, basedir+"/alignments")

def unfurl_alignments(alignments_file, file_list, output_dir):
    '''
    We assume a hard one-to-one correspondence of the tagged_strings and the
    file_list. Everything falls apart if this is not true.
    '''

    print("Unfurling alignments ...")

    handle = open(alignments_file)
    alignments = handle.readlines()
    handle.close()
    fl_counter = 0

    for i in range(0, len(alignments), 2):
        filename = file_list[fl_counter]
        filename = filename.replace(".desc", ".align")
        print(filename)
        print(alignments[i][:-1])
        print(alignments[i+1][:-1])
        single_file = open(output_dir + "/" + filename, "w")
        single_file.write(alignments[i])
        single_file.write(alignments[i+1])
        single_file.close()
        fl_counter+=1          

    print("... done")

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

    atype = "lexical"
    try:
        atype = args['-a']
    except KeyError:
        print "Assuming lexical alignments"
 
    # Find the alignments between the source and target words
    detect_alignments(atype, dir+"/source-strings-tagged", dir+"/target-strings", dir)
    files = sorted([x for x in os.listdir(text_dir) if x.endswith(".desc")])
    unfurl_alignments(dir+"/alignments", files, dotfiles_dir)

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
