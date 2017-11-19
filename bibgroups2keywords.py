#!/usr/bin/env python
import re
import utils
from xml.etree import ElementTree
import json
import argparse
import subprocess
import plistlib
import base64
import bibtexparser
import timeit
import datetime
import dateutil.parser

#from Foundation import NSPropertyListSerialization, NSData, NSPropertyListXMLFormat_v1_0


# TODO
# - AppKit connect to BibDesk to rename static groups
#   in alternative I can work on the XML and replace it into the .bib but might be dangerous with BibDesk open
# - AppKit connec to BibDesk to add items to static groups (really needed?)


VERSION=0.3

def DEBUG():
    return True

def bibtex2dictionary(file_name):
    with open(file_name) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    return bib_database.get_entry_dict()

def findBdsk_File_N(n,bibtex_dic,bibitem):
    base64str=""
    if DEBUG(): print "working on ", bibitem
    _item="bdsk-file-"+str(n)
    try:
        base64str=bibtex_dic[bibitem][_item]
    except KeyError:
        base64str=""

    return base64str

def bibitem2paths(bibitem,bibitem_dic):
    attempt=0
    relative_paths=[]
    base64path=''
    while base64path != '' or attempt==0:
        attempt=attempt+1
        base64path=findBdsk_File_N(attempt,bibitem_dic,bibitem)
        if base64path != '':
            relative_path=convertBase64alias2relativePath(base64path,bibitem)
            relative_paths.append(relative_path)
    return relative_paths

def convertBase64alias2relativePath(base64path,bibitem):
    res = subprocess.check_output(["./base64xml.sh", base64path, bibitem])
    #print base64.b64decode(base64path)
    _xmlpath=bibitem+".xml"
    _xml_dic=plistlib.readPlist(_xmlpath)
    #for k,v in _xml_dic.items():
    #    print k
    relative_path=_xml_dic["$objects"][4]
    #print relative_path
    #data_absolute_path=_xml_dic["$objects"][5]['NS.data']
    #print data_absolute_path
    #print base64.b64decode(data_absolute_path)
    res = subprocess.check_output(["rm", _xmlpath])
    _xmlpath
    return relative_path

def get_epoch_time_of_bibitem(bibitem,bibitem_dic):
    _a_human_time=bibitem_dic[bibitem]["date-modified"] # format is 2017-11-19 16:42:59 +0000
    _mod_time=dateutil.parser.parse(_a_human_time)
    #_format="%Y-%m-%d %H:%M:%S +%f"
    #_mod_time=datetime.datetime.strptime(_a_human_time, _format)
    #print _a_human_time
    #print _mod_time.strftime("%A, %d. %B %Y %I:%M%p")
    return _mod_time.strftime("%s")

def add_keywords_to_group_members(groupname,Groups,bibitem_dic):
    for bibitem in Groups[groupname]:
        #print bibitem_dic[bibitem]
        mtime=get_epoch_time_of_bibitem(bibitem,bibitem_dic)
        relative_paths=bibitem2paths(bibitem,bibitem_dic)
        for path in relative_paths:
            group_word="G:"+groupname
            if DEBUG(): print 'Adding the g-keyword ', groupname, ' to ' , path
            res = subprocess.check_output(["pyXattr.py","-a", group_word, "-f", path, "-m", mtime])
            res = subprocess.check_output(["tag","-a",group_word, path])

def file2xml_lines(file_name):
    _xml_groups=[]
    file = open(file_name,"r")
    for line in file:
        _xml_groups.append(line)
    return _xml_groups

def file2xml_tagged_lines(file_name):
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
    epilog = """
    It can take a bibtex file and make an XML file with the content of the Bibdesk Static Groups.
    It can print the print bibitem of the members of a named group or of all groups. It can print the relative path of a PDF file in a bibitem.
    It can add
    """
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
    if DEBUG(): print "working on ", file_name
    xml_groups=[]
    if len(file_name)>0:
        xml_groups=file2xml_tagged_lines(file_name)

    if write_xml_to_file:
        utils.write_lines_to_file(xml_groups,"mylines.xml")


    Groups=xml_lines2dic(xml_groups)


    if groups2keyword:

        start_time = timeit.default_timer()
        bibitem_dic=bibtex2dictionary(file_name)
        end_time= timeit.default_timer()
        print "Parsing the bibtex file ", file_name, " took ",   end_time - start_time, " seconds"

        if all_groups:
            for g,p in Groups.items():
                print "Working on group ", g,": ",p
                try:
                    if len(Groups[g])>0:
                        add_keywords_to_group_members(g,Groups,bibitem_dic)
                except KeyError:
                    print "group ", g," is empty."
                    
        elif len(groupname)>0:
            if len(Groups[groupname])>0:
                print Groups[groupname]
                add_keywords_to_group_members(groupname,Groups,bibitem_dic)


if __name__ == '__main__':
    main()
