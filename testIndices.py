import sys
import re

for line in open(sys.argv[1]):
    (sid, uid, si, ei, sentiment, text) = line.strip().split('\t')
    si = int(si)
    ei = int(ei)
    
    if text == "Not Available":
        continue
    
    #print str(text.split(' '))

    words = [x for x in text.split(' ') if x != '']
    if words[0] == "RT" and words[1][0] == '@':
        words = words[2:]

    print "\t".join([text, str(si), str(ei), " ".join(words[si:ei+1])])
