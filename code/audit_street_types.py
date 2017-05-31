
"""
This file audits street names in the Austin, TX, metro extra from OpenStreetMap. It collects lists streets
of streets as values in a dictionary under the last word that appears in the street address as a key,
thus allowing the user to see groupings of street names. Additionally, it includes a mapping to that 
can be used to replace abbreviations with their full-text words and an update function to do so.
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSM_FILE = "sample.osm"

# Captures "street name" by picking up the last "word" in a street address.
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]


mapping = { "st": "Street",
            "ave": "Avenue",
            "rd": "Avenue",
            "ln": "Lane", # Newly added abbrev mappings based on Austin, TX data.
            "ct": "Court",
            "cv": "Cove",
            "dr": "Drive",
            "pl": "Place",
            "trl": "Trail"}


def audit_street_type(street_types, street_name):
    ''
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit_street_types(osm_file):
    osm_file = open(osm_file, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "way":  # Only consider "way" tags
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_street_name(name, mapping):
    name_list = name.split(' ')
    for i,word in enumerate(name_list):
        word = word.split('.')[0].lower() # Remove periods and set lowercase
        if word in mapping:
            name_list[i] = mapping[word]
            name = ' '.join(name_list)
    return name

if __name__ == '__main__':
    st_types = audit_street_types(OSM_FILE)
    pprint.pprint(dict(st_types))