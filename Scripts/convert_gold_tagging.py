import re
import pdb
import codecs
import sys

"""
convert_gold_tagging.py
Derek Salama and Jake Leichtling

This script converts the Penn Tree Bank corpus into the output format
of our Viterbi algorithm: (word_1,pos_1) (word_2,pos_2) ...

Usage:
    python convert_gold_tagging.py ptb_file output_file_name
"""

# output format:
# (token,tag) (token, tag)....

def convert(input_file_name, output_file_name):
    inputf = codecs.open(input_file_name, 'r', 'utf8')
    outf = codecs.open(output_file_name, 'w', 'utf8')

    for line in inputf:
        # skip blank lines
        if line is None:
            continue

        # remove any whitespace to the left or right
        line = line.lstrip()
        line = line.rstrip()

        # use '=============' as line delimiters
        if len(line.replace("=", "")) == 0 and len(line) != 0:
            outf.write("\n")
            continue

        # remove brackets (that have no semantic meaning)
        line = line.replace("[", "")
        line = line.replace("]", "")


        tokens = line.split()
        tokenPairs = map(lambda token: re.split(r"(?<!\\)/", token, 1), tokens)

        for tokenPair in tokenPairs:
            #only consider words, not punctuation
            if tokenPair[0] != tokenPair[1] and re.sub("[^a-zA-Z0-9]", "", tokenPair[0]) != "":
                outf.write("(" + tokenPair[0] + ",")

                # for now, only choose the first tagging for evaluation
                states = re.split("\|", tokenPair[1])
                outf.write(states[0] + ") ")

    inputf.close()
    outf.close()

if __name__=='__main__':
    pos_file = sys.argv[1]
    output_file_name = sys.argv[2]

    convert(pos_file, output_file_name)
