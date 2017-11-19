#!/usr/bin/env python

import re
import utils
from xml.etree import ElementTree
import json
import argparse
# takes a bibtex file and makes a XML file with the content of the Bibdesk Static Groups
VERSION=0.1

def DEBUG():
    return True

def file2xml_lines(file_name):
    static_groups_group=False
    _xml_groups=[]
    file = open(file_name,"r")
    for line in file:
        if  static_groups_group:
            if "}" in line:
                static_groups_group=False
                if DEBUG(): print "ending static group block"
        if  static_groups_group:
            _xml_groups.append(line)
        if "@comment{BibDesk Static Groups{" in line:
            if DEBUG():  print line," found"
            static_groups_group=True
    return _xml_groups

def xml_lines2dic(xml_groups):
    '''
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <array>
        	<dict>
        		<key>group name</key>
        		<string>CLIC BSM</string>
        		<key>keys</key>
        		<string>Cheng:2016ay,Rawat:2017ir</string>
        	</dict>
    '''
    xml_string=''.join(xml_groups)
    root = ElementTree.fromstring(xml_string)
    array=root[0]
    _Groups={}
    for dic in array:
        group_name=str(dic[1].text)
        if ',' in str(dic[3].text):
            _Groups[group_name]=dic[3].text.split(',')
        else:
            try:
                _Groups[group_name]=[str(dic[3].text)]
            except TypeError:
                _Groups[group_name]=[]
                print str(dic[1].text), ' IS EMPTY'
    return _Groups

def main():
    usage = """Usage: %prog [options]"""
    epilog = ""
    parser = argparse.ArgumentParser(usage=usage, version=VERSION,
                                   epilog=epilog)

    parser.add_argument(
        '-k', '--groups2keyword',
        default=False, action="store_true",
        help="Write a keyword named as the group for each file member of a group.")
    parser.add_argument(
        '-a', '--all_groups',
        default=False, action="store_true",
        help="Loop over all the groups")
    parser.add_argument(
        '-g', '--group', default="",
        help="Group on which to operate")
    parser.add_argument(
        '-w', '--write_xml',
        default=False, action="store_true",
        help="Write to file the XML extracted from the bibtex comments")
    parser.add_argument(
        '-b', '--bib', default="test.bib",
        help="bibtex file to be processed")

    args = parser.parse_args()
    #################################
    write_xml_to_file=args.write_xml
    file_name=args.bib
    groups2keyword=args.groups2keyword
    groupname=args.group
    all_groups=args.all_groups
    #################################
    xml_groups=[]
    if len(file_name)>0:
        xml_groups=file2xml_lines(file_name)

    if write_xml_to_file:
        utils.write_lines_to_file(xml_groups,"mylines.xml")


    Groups=xml_lines2dic(xml_groups)

    #groupname='AMS photons'
    if groups2keyword:
        print Groups[groupname]

    #    Groups[str(dic[1].text)]=list(dic[3].text)
    #xml.find(".//*[@tag='001']")
    #xml_dict=xmltodict.parse(xml_string)
    #print(json.dumps(result, indent=4))
    #with open(file_name, 'r') as myfile:
    #    string_data=myfile.read().replace('\n', '')

if __name__ == '__main__':
    main()
