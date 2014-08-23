#!/bin/sh

# You need the following dependencies for this to script to work
# maltparser-1.7.2
# stanford-postagger-2012-01-06

python textPOSTag.py -p ../rawData
python testParse.py -p ../rawData
python imageAnnotationExtractions.py -p ../rawData
python imageAlignWithText.py -p ../rawData  
