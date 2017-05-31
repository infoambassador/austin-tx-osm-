#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint

OSM_FILE = 'sample.osm'

def find_children_and_tags(filename):
    ''' Takes an OSM file and returns a dictionary whose keys are
    tags in the OSM file and whose values are lists of the children
    tags of the keys.
    '''
    
    current_path = []
    tag_children = defaultdict(set)
    context = ET.iterparse(filename, events=("start","end"))
    
    for event, elem in context:
        if event == "start":
            if current_path:
                tag_children[current_path[-1]].add(elem.tag)
            current_path.append(elem.tag)
        else:
            current_path.pop()
    return tag_children
    
if __name__ == "__main__":
    pprint.pprint(dict(find_children_and_tags(OSM_FILE)))