
''' This script takes an OSM file and parses it into a collection 
of CSV files adhering to an elsewhere-defined SQL database schema.
During the reshaping of the data, it applies a cleaning scripts
from audit_phone_formats.py and audit_street_types.py.

'''

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import audit_phone_formats
import audit_street_types



OSM_PATH = "sample.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"
RELATIONS_PATH = 'relations.csv'
RELATIONS_TAGS_PATH = 'relations_tags.csv'
RELATIONS_NODES_PATH = 'relations_nodes.csv'
RELATIONS_WAYS_PATH = 'relations_ways.csv'

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

mapping = { "st": "Street",
            "ave": "Avenue",
            "rd": "Avenue",
            "ln": "Lane", # Newly added abbrev mappings based on Austin, TX data.
            "ct": "Court",
            "cv": "Cove",
            "dr": "Drive",
            "pl": "Place",
            "trl": "Trail"}


# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']
RELATION_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
RELATION_NODES_FIELDS = ['id', 'node_id']
RELATION_WAYS_FIELDS = ['id', 'way_id']
RELATION_TAGS_FIELDS = ['id', 'key', 'value', 'type']

def shape_element(element, node_fields=NODE_FIELDS, way_fields=WAY_FIELDS,
                   relation_fields = RELATION_FIELDS, problem_chars=PROBLEMCHARS,
                  default_tag_type='regular'):
    """Clean and shape node, way or relation XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for node, way, relation elements
    relation_attribs = {}
    relation_nodes = []
    relation_ways = []
    
    # Handles TAG child tags for NODES, WAYS, and RELATIONS.
    for tag in element.iter("tag"):
        if PROBLEMCHARS.search(tag.attrib['k']) is None:
            tag_dict = {'id':element.attrib['id'], 'key':tag.attrib['k'], 'type':'regular', 'value':tag.attrib['v']}
            if tag.attrib['k'] == "phone":
                tag_dict['value'] = audit_phone_formats.update_phone_number(tag.attrib['v'])
            if tag.attrib['k'] == "addr:street":
                tag_dict['value'] = audit_street_types.update_street_name(tag.attrib['v'],mapping)
            tags.append(tag_dict)
                
    # Handles ND child tags of WAYS
    for i,nd in enumerate(element.iter("nd")):
        nd_dict = {'id':element.attrib['id'], 'node_id':nd.attrib['ref'], 'position':i}
        way_nodes.append(nd_dict)
    
    # Handles MEMBER child tags of RELATIONS
    for i,member in enumerate(element.iter("member")):
        mem_type = member.attrib['type']
        mem_dict = {'id':element.attrib['id'], mem_type+'_id':member.attrib['ref']}
        if mem_type == "way":
            relation_ways.append(mem_dict)
        elif mem_type == "node":
            relation_nodes.append(mem_dict)
    
    # Processes NODE tags
    if element.tag == 'node':
        node_attribs = {attrib:element.attrib[attrib] for attrib in element.attrib if attrib in node_fields}
        return {'node': node_attribs, 'node_tags': tags}
    
    # Processes WAY tags
    elif element.tag == 'way':
        way_attribs = {attrib:element.attrib[attrib] for attrib in element.attrib if attrib in way_fields}
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

    # Processes RELATION tags
    elif element.tag == 'relation':
        relation_attribs = {attrib:element.attrib[attrib] for attrib in element.attrib if attrib in relation_fields}
        return {'relation':relation_attribs, 'relation_nodes':relation_nodes, 'relation_ways':relation_ways, 'relation_tags':tags}
    
# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
        codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
        codecs.open(WAYS_PATH, 'w') as ways_file, \
        codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
        codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file, \
        codecs.open(RELATIONS_PATH, 'w') as relations_file, \
        codecs.open(RELATIONS_TAGS_PATH, 'w') as relations_tags_file, \
        codecs.open(RELATIONS_WAYS_PATH, 'w') as relations_ways_file, \
        codecs.open(RELATIONS_NODES_PATH, 'w') as relations_nodes_file:
        
        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)
        relation_writer = UnicodeDictWriter(relations_file, RELATION_FIELDS)
        relation_nodes_writer = UnicodeDictWriter(relations_nodes_file, RELATION_NODES_FIELDS)
        relation_ways_writer = UnicodeDictWriter(relations_ways_file, RELATION_WAYS_FIELDS)
        relation_tags_writer = UnicodeDictWriter(relations_tags_file, RELATION_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()
        relation_writer.writeheader()
        relation_nodes_writer.writeheader()
        relation_ways_writer.writeheader()
        relation_tags_writer.writeheader()


        for element in get_element(file_in, tags=('node', 'way','relation')):
            el = shape_element(element)
            if element.tag == 'node':
                nodes_writer.writerow(el['node'])
                node_tags_writer.writerows(el['node_tags'])
            elif element.tag == 'way':
                ways_writer.writerow(el['way'])
                way_nodes_writer.writerows(el['way_nodes'])
                way_tags_writer.writerows(el['way_tags'])
            elif element.tag == 'relation':
                relation_writer.writerow(el['relation'])
                relation_nodes_writer.writerows(el['relation_nodes'])
                relation_ways_writer.writerows(el['relation_ways'])
                relation_tags_writer.writerows(el['relation_tags'])


if __name__ == '__main__':
    process_map(OSM_PATH)