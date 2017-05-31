
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET  

OSM_FILE_PATH ="/"
OSM_FILE = OSM_FILE_PATH+"austin_texas.osm"  	# Austin, TX metro extract
SAMPLE_PATH = "/"
SAMPLE_FILE = "sample.osm" 		# Sample file

k = 150 # Parameter: take every k-th top level element, tuned to produce < 10MB file

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def create_sample(osm_file,sample_file):
    """Takes an xml file and creates a sample of the top level tags therein by
    taking a systematic sample.
    """
    
    with open(sample_file, 'wb') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<osm>\n  ')

        # Write every kth top level element
        for i, element in enumerate(get_element(osm_file)):
            if i % k == 0:
                output.write(ET.tostring(element, encoding='utf-8'))
        output.write('</osm>')
    pass
    
if __name__ == '__main__':
    create_sample(PATH+OSM_FILE,SAMPLE_FILE)
    print('Sample created in {}.'.format(SAMPLE_FILE))
