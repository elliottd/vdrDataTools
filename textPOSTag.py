import os
import re
import sys
import getopt
import subprocess

options = ["-p", "-h", "-a"] # -h is reserved.
stanford = "stanford-postagger-2012-01-06"
malt = "maltparser-1.7.2"

def concatenate_text(path, extension, output_file):
    '''
    Concatenate a collection of files with a given extension into
    the output_file.
    '''
    print("cat %s/*.%s ..." % (path, extension))
    os.system("cat %s/*.%s > %s-tmp" % (path, extension, output_file))
    destination = open("%s" % (output_file), "w")
    for line in open("%s-tmp" %(output_file)).readlines():
        new_line = re.sub(r'\.(\w)', r'.\n\1', line)
        destination.write(new_line)
    destination.close()
    print("... done.")
    print
    
def to_conll_format(input_file):
    '''
    Converts the POS tagged input file into CoNLL format. 
    Required by the MALT parser.
    '''

    data = open(input_file).readlines()
    output = open("%s-conll" % input_file, "w")

    for line in data:
        line = line.split(" ")
        for idx, pair in enumerate(line):
            word = pair.split("_")[0]
            tag = pair.split("_")[1].strip("\n")
            output.write("%d\t%s\t%s\t%s\t%s\t_\t_\t_\t_\t_\n" % (idx, word, word, tag, tag))
        output.write("\n")

    output.close()
            

def pos_tag(path, input_file):
    '''
    Part-of-speech tag the text file into input_file-tagged
    '''

    print("Tagging ...")
    cmd = ["java -mx1024m -classpath %s/stanford-postagger.jar edu.stanford.nlp.tagger.maxent.MaxentTagger -model %s/models/english-bidirectional-distsim.tagger -textFile %s/%s > %s/%s-tagged" % (stanford, stanford, path, input_file, path, input_file)]
    subprocess.call(cmd, shell=True)
    print("... done.")
    print

def unfurl_tags(tagged_strings_file, file_list, output_dir):
    '''
    The POS tagger needs to receive all sentences at the same time to make 
    tagging computationally efficient.
    
    We unfurl the line-by-line sentences into a set of files. Each description
    contains two (2) sentences so we process the tagged_strings file in pairs
    and output each pair to a file with a .malt extension.

    We assume a hard one-to-one correspondence of the tagged_strings and the
    file_list. Everything falls apart if this is not true.
    '''

    print("Unfurling tagged files ...")

    tagged_strings = open(tagged_strings_file).readlines()
    fl_counter = 0

    for i in range(0, len(tagged_strings), 2):
        filename = file_list[fl_counter]
        filename = filename.replace(".desc", ".tagged")
#        print(filename)
#        print(tagged_strings[i][:-1])
#        print(tagged_strings[i+1][:-1])
        single_file = open(output_dir + "/" + filename, "w")
        single_file.write(tagged_strings[i])
        single_file.write(tagged_strings[i+1])
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
    concatenate_text(text_dir, "desc", dir+"/source-strings")
    pos_tag(dir, "source-strings")
    files = sorted([x for x in os.listdir(text_dir) if x.endswith(".desc")])
    unfurl_tags(dir+"/source-strings-tagged", files, text_dir)

def usage():
    # This function is used by process_arguments to echo the purpose and usage 
    # of this script to the user. It is called when the user explicitly
    # requests it or when no arguments are passed

    print
    print("textPOSTag takes the original data and POS tags the descriptions") 
    print
    print("Usage: python testPOSTag.py -p {path to original data}")
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
