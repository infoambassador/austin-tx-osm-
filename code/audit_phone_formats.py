
''' This script audits phone number formatting by creating and displaying
a dictionary showcasing the various characters joining digit blocks 
in phone numbers in the data and their frequencies. '''

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

osm_file = "sample.osm"

# Reg exp for extracting connection types from phone number
con = r'([\D|\s]*)'        # Captures symbols joining digit blocks
country = r'\+?\d?\d?'      # Country code (optional)
area = r'\d{3}'             # Area code
prefix = r'\d{3}'           # Prefix
line = r'\d{4}'             # Line number
phone_con_string = country+con+area+con+prefix+con+line
phone_con_re = re.compile(phone_con_string)

# Reg exp for extracting country, area, prefix, line
con = r'[\D|\s]*'                 # Various connectors and spaces between parts of phone number
country = r'(?P<country>\d{1,2})?' # Country code (optional)
area = r'\(?(?P<area>\d{3})\)?'    # Area code
prefix = r'(?P<prefix>\d{3})'      # Prefix
line = r'(?P<line>\d{4})'          # Line number
phone_digits_string = country+con+area+con+prefix+con+line
phone_digits_re = re.compile(phone_digits_string)


## HELPER FUNCTIONS

def audit_phone_format(phone_formats, phone_number):
    ''' Adds entry to dict phone_formats whose keys are strings 
    containing the connectors found between blocks of digits in US 
    phone numbers and whose values are sets of phone numbers
    consistent with that string.
    
    E.g., '[() -]':Set([(832) 588-8683])
    '''
    n = phone_con_re.search(phone_number)
    if n:
        phone_format = '['+''.join(n.groups())+']'
        phone_formats[phone_format].add(phone_number)

def is_phone_number(elem):
    ''' Indicates <tag...> elements with attrib "phone".
    Returns True/False.
    '''
    return (elem.tag =="tag") and (elem.attrib['k'] == "phone")
            
def update_phone_number(phone_number):
    ''' Uses regex to capture area code, prefix, and line number from
    phone_number string and reformat it into "(area) prefix - line" format.
    '''
    
    m = phone_digits_re.search(phone_number)
    if m:
        phone_number = '({}) {} - {}'.format(m.group('area'),m.group('prefix'),m.group('line'))
        return phone_number
    return phone_number

## MAIN PHONE AUDITING FUNCTION

def audit_phone_formats(osm_file):
    ''' Main function that ties together phone audit procedure.
    '''
    
    osm_file = open(osm_file,'r')
    phone_formats = defaultdict(set)
    
    for event, elem in ET.iterparse(osm_file):
        if is_phone_number(elem):
            print(update_phone_number(elem.attrib['v']))
            audit_phone_format(phone_formats, elem.attrib['v'])
    osm_file.close()
    return phone_formats

if __name__ == '__main__':
    phone_formats = audit_phone_formats(osm_file)
    pprint.pprint(dict(phone_formats))