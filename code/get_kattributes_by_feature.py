#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint

OSM_FILE = 'sample.osm'

def get_kattributes_by_feature(filename):
    ''' Takes an OSM file and dictionary whose keys are 'node',
    'way' and 'relation' (the major features of the OSM file)
    and whose values are dictionaries containing the various
    k-attributes of child <tag...> elements and whose values are
    their counts.
    '''

    kattributes_by_feature = {'node':defaultdict(int),
                              'way':defaultdict(int),
                              'relation':defaultdict(int)}
    
    context = ET.iterparse(filename, events=("start",))
    
    for event, elem in context:
        if elem.tag in ['node','way','relation']:
            for tag in elem.iter('tag'):
                kattributes_by_feature[elem.tag][tag.attrib['k']] += 1
    return kattributes_by_feature

if __name__ == "__main__":
    pprint.pprint(dict(get_kattributes_by_feature(OSM_FILE)['node']))