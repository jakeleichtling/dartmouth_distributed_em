from __future__ import division
import pdb
import codecs
import sys
import re
from collections import defaultdict

def parse_tagging(file_name):
    inputf = codecs.open(file_name, 'r', 'utf8')

    total_tagging = []
    for line in inputf:
        # skip empties
        if len(line) <= 0:
            continue

        for pair in line.split():
            m = re.match(r"\((.*),(.*)\)", pair)
            tag = m.group(2)
            total_tagging.append(tag)

    return total_tagging

def create_tag_map(hmm_tags, gold_tags):
    maximum_map = dict()
    for tag in set(hmm_tags): # iterate through unique tags
        cooccurrence_count = defaultdict(int)

        for (hmm_t, gold_t) in zip(hmm_tags, gold_tags):
            if hmm_t == tag:
                cooccurrence_count[gold_t] += 1

        maximum_cooccurrance = max(cooccurrence_count.iterkeys(),
                key=(lambda key: cooccurrence_count[key]))
        maximum_map[tag] = maximum_cooccurrance

    return maximum_map

def num_correct(hmm_to_gold, hmm_tags, gold_tags):
    correct = 0
    for (hmm_t, gold_t) in zip(hmm_tags, gold_tags):
        if hmm_to_gold[hmm_t] == gold_t:
            correct += 1

    return correct

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

