# austin-tx-osm

## Synopsis

- This project explores processing a large (1.43 GB) OpenStreetMap extract for the Austin, TX Metropolitan Area. A few fields are audited and cleaned using Python 2.7 code. Suggestions for additional improvements to the data set are included.

- Link to Austin, TX, relation on OpenStreetMap: http://www.openstreetmap.org/relation/113314
- Link to metro extract download on MapZen: https://mapzen.com/data/metro-extracts/metro/austin_texas/

## Process Overview (by way of scripts)

1. create_sample.py
   - Systematically samples an XML file (with a tunable parameter, k) and writes a new XML file.
2. count_tags.py
   - Iteratively parses an XML file and stores the top-level XML tags and their counts as key-value pairs in a dictionary.
3. find_children_and_tags.py
   - Iteratively parses an XMl file and creates a dictionary of top-levle tags and sets of their children as key-value pairs in a dictionary.
4. get_kattributes_by_feature.py
   - Iteratively parses an XML file of OSM data and creates dictionary of k-attributes of child tags and their counts as key-value pairs for nodes, ways, and relations.
5. audit_street_types.py
   - Iteratively parses an XML of OSM data and creates dictionary of street types (by capturing last word from streets names in addresses) and sets of street names containing that street type as key-value pairs.
   - Includes a function called update_street_types (code below) that employs a mapping between street abbreviations present in the Austin, TX, metro extract and the full words to update the street types in the data set.

```python
def update_street_name(name, mapping):
    name_list = name.split(' ')
    for i,word in enumerate(name_list):
        word = word.split('.')[0].lower() # Remove periods and set lowercase                                                   
        if word in mapping:
            name_list[i] = mapping[word]
            name = ' '.join(name_list)
    return name
```
6. audit_phone_formats.py
   - Iteravely parses an XML file of OSM data and creates dictionary of telephone number "formatting strings" and sets of phone numbers coinciding with that formatting string. "Formatting strings" are the set of characters (including whitespace) between blocks of digits in a telephone. E.g., (555) 555- 5555 would have the phone formatting string '[() - ]'.
   - Includes a function called update_phone_number (code below) that extracts the blocks of digits from a phone number and returns a phone number with the formatting (555) 555 - 5555.

```python
# Reg exp for extracting country, area, prefix, line                                                                           
con = r'[\D|\s]*'                 # Various connectors and spaces between parts of phone number                                
country = r'(?P<country>\d{1,2})?' # Country code (optional)                                                                   
area = r'\(?(?P<area>\d{3})\)?'    # Area code                                                                                 
prefix = r'(?P<prefix>\d{3})'      # Prefix                                                                                    
line = r'(?P<line>\d{4})'          # Line number                                                                               
phone_digits_string = country+con+area+con+prefix+con+line
phone_digits_re = re.compile(phone_digits_string)

def update_phone_number(phone_number):
    ''' Uses regex to capture area code, prefix, and line number from                                                          
    phone_number string and reformat it into "(area) prefix - line" format.                                                    
    '''

    m = phone_digits_re.search(phone_number)
    if m:
        phone_number = '({}) {} - {}'.format(m.group('area'),m.group('prefix'),m.group('line'))
        return phone_number
    return phone_number
```

7. process_osm_file.py
   - Iteratively parses XML file of OSM data, applying cleaning routines in audit_street_types.py and audit_phone_formats.py.
   - Writes processed data into CSV files to be later uploaded to a SQLite database.
