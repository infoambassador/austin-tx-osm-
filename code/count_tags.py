#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint

OSM_FILE = 'sample.osm'

def count_tags(filename):
    ''' Takes an OSM file and returns a dictionary containing the top
    level tags for the file and their counts.
    '''
    
    tags = defaultdict(int)
    context = ET.iterparse(filename, events=("start",))

    for event, elem in context:
        tags[elem.tag] += 1
    return tags

if __name__ == "__main__":
    pprint.pprint(dict(count_tags(OSM_FILE)))