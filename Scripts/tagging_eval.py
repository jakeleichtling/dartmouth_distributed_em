from __future__ import division
import pdb
import codecs
import sys
import re
from collections import defaultdict

"""
tagging_eval.py
Derek Salama and Jake Leichtling

This script determines the accuracy of a part-of-speech tagging,
given the Viterbi output and gold-standard tagging for the same
corpus.

We align the HMM states with parts of speech by finding the part
of speech each state cooccurs most frequently with. Once we have
this association, we calculate the ratio of words that have been
correctly tagged.

This evalutaion, of course, requires that the Viterbi output be
in the same order as the input. Because we cannot enforce this
ordering in a distributed system, this script also sorts the
Viterbi output by the "byte-offset" included at the start of
each line.

Usage:
    python tagging_eval.py viterbi_output_file sorted_output_file gold_tagging_file
    
Where viterbi_output_file is the output of our Viterbi implmentation, sorted_output_file
is an intermediate file where we will write the tagging in sorted order, and gold_tagging_file
is the Penn Tree Bank gold-standard tags converted into the proper format by the
conver_gold_tagging.py script.
"""

# Given the lines of input in (word,pos) format, creates an
# ordered list of all the parts of speech tags.
def parse_tagging(file_name):
    inputf = codecs.open(file_name, 'r', 'utf8')

    total_tagging = []
    for line in inputf:
        # skip empties
        if len(line) <= 0:
            continue

        for pair in line.split():
            m = re.match(r"\((.*),(.*)\)", pair)
            tag = m.group(2) # just get the tag
            total_tagging.append(tag)

    return total_tagging

# Given the ordered list of viterbi tags and gold-standard tags,
# create a mapping between the two by finding the gold-standard
# tag that each state coccures most frequently with
def create_tag_map(hmm_tags, gold_tags):
    maximum_map = dict()
    for tag in set(hmm_tags): # iterate through unique tags
        cooccurrence_count = defaultdict(int)

        for (hmm_t, gold_t) in zip(hmm_tags, gold_tags):
            if hmm_t == tag:
                cooccurrence_count[gold_t] += 1

        # Find the max by the cooccurence count
        maximum_cooccurrance = max(cooccurrence_count.iterkeys(),
                key=(lambda key: cooccurrence_count[key]))
        maximum_map[tag] = maximum_cooccurrance

    return maximum_map

# Given the hmm_to_gold mapping, and ordered viterbi and gold standard
# output, simply count the number of times it is correct
def num_correct(hmm_to_gold, hmm_tags, gold_tags):
    correct = 0
    for (hmm_t, gold_t) in zip(hmm_tags, gold_tags):
        if hmm_to_gold[hmm_t] == gold_t:
            correct += 1

    return correct

# Sort the lines from the distributed algorithm by
# the byte offset of those lines
# (as was recorded in the original output)
def sort_lines(file_name, output_name):
    inputf = codecs.open(file_name, 'r', 'utf8')
    outputf = codecs.open(output_name, 'w', 'utf8')

    lines = []
    for line in inputf:
        lines.append(line)

    offset_lines = map(lambda line: re.split(":", line, 1), lines)
    offset_lines.sort(lambda x,y: cmp(int(x[0]), int(y[0])))

    for offset_line in offset_lines:
        outputf.write(offset_line[1].strip() + "\n")

    outputf.close()

if __name__=='__main__':
    hmm_output_file = sys.argv[1]
    sorted_hmm_output_file = sys.argv[2]
    gold_tagging_file = sys.argv[3]

    sort_lines(hmm_output_file, sorted_hmm_output_file)

    hmm_tags = parse_tagging(sorted_hmm_output_file)
    print len(hmm_tags)

    gold_tags = parse_tagging(gold_tagging_file)
    print len(gold_tags)

    hmm_to_gold_tags = create_tag_map(hmm_tags, gold_tags)
    print hmm_to_gold_tags
    print hmm_tags[0]
    print gold_tags[0]
    correct = num_correct(hmm_to_gold_tags, hmm_tags, gold_tags)

    print "PERCENT CORRECT: ",
    print correct / len(hmm_tags)

