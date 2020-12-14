#!/usr/bin/env python3.7

import time
import datetime, time
import json
import utils
import argparse
import subprocess
import sys, os
import utils
from beautifultable import BeautifulTable
import pandas as pd
import os.path
from pyXattr_utils import *
# manipulate a JSON list contained in the xattr called pyXattr
# keep track of the same in a python dictionary serialized at $KikDeskFile

# TODO

def load_configuration(json_data):
    the_dict=load_current_json_as_dict(json_data)
    globals().update(the_dict)
    print(the_dict)

VERSION=0.5

try:
    load_configuration('config.json')
except FileNotFoundError:
    #### output format and options ####
    short_date_format='%Y-%m-%d'
    long_date_format='%Y-%m-%d %H:%M'
    recent_days=0.5
    KikDeskFile="/Users/roberto/Dropbox/BibReader/Tags.kik"


class optionsSet():
    """just a data structure to move around options that affect the behaviour of the program"""
    def __init__(self):
        self.sync = True


class kikData():
    """just a data structure to move around tags and bibitem information"""
    def __init__(self):
        self.tags = ""
        self.bibitem = ""
        self.mtime = ""



# TODO
# option to use this script that implies the same operation is done on OS X tags usings
# tag -a file
# tag -r file
# TODO
# add a function to change the keyword field of the bibtex file, possibly through BibDesk, which is likely to be concurrently using the file, hence better not pass above it.

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "-t", "--add_tag", default="", help="tags to be added. CSV format")
    parser.add_argument("-r", "--remove_tag", default="", help="tags to be removed. CSV format")
    parser.add_argument('--not_sync_osx', default=True, action="store_false", help="do not call tag utility to keep in sync the OS X tags (which are accessible in Finder and searchable via spotlight tag: )")
    parser.add_argument('-f', '--filename', default="", help="file to be processed")
    parser.add_argument("-b", "--bibitem", default="", help="bibitem string to be added as a tag")
    parser.add_argument("-m", "--mtime", default="", help="epoch time at which to place the time info of the tag")
    parser.add_argument('-l', '--list', default=False, action="store_true", help="list recently used tags putting most revent the bottom of the  list")
    parser.add_argument('-s', '--short', default=False, action="store_true", help="keep list minimal as to pass it to further parsing")
    parser.add_argument("--search", default="", help="print full table row for the tag matching exactly this string")
    #args = parser.parse_args()
    args = parser.parse_args(args)
    ###################################
    filename=args.filename
    listing=args.list
    short_listing=args.short
    m_time=args.mtime
    bibitem=args.bibitem
    search_string=args.search
    grow=len(args.add_tag)
    shrink=len(args.remove_tag)
    tags=""
    if grow > 0:
        tags=args.add_tag
    if shrink > 0:
        tags=args.remove_tag

    ###################################

    if (len(filename)>0):
        #get the current tag value. it is a is a list of dictionaries
        initial_kik_set = get_current_pyXattr(filename)
    if len(tags)>0: # is the same as saying -a or -d  was provided
        kik=kikData()
        kik.bibitem=bibitem
        kik.tags=tags
        kik.mtime=m_time


        if grow > 0:
            # extend the tags
            working_tags_set=extend_tags(initial_kik_set,kik)

        if shrink > 0:
            # reduce the tags
            working_tags_set=remove_tags(initial_kik_set,kik)

        # make the tags into JSON
        pyXtag=json.dumps(working_tags_set)
        # write the tags
        print( "writing ", pyXtag)
        res = subprocess.check_output(["xattr", "-w", "pyXattr", pyXtag, str(filename)])
        for line in res.splitlines():
            print( line)

        # update the kikDB, valid for both grow or shrink
        kikdesk_file_exists=os.path.isfile(KikDeskFile)
        if not kikdesk_file_exists:
            _emptydic={}
            serialize_dict_to_file_as_json(_emptydic,KikDeskFile)

        current_kikdb=load_current_json_kikdeskfile(KikDeskFile)
        serialize_dict_to_file_as_json(current_kikdb,KikDeskFile+".back")

        if DEBUG(): print( current_kikdb)
        new_kikdb=current_kikdb
        new_kikdb[str(filename)]=working_tags_set
        serialize_dict_to_file_as_json(new_kikdb,KikDeskFile)

    if listing:
        current_kikdb=load_current_json_kikdeskfile(KikDeskFile)
        list_tags, df_tags = list_tags_in_reverse_time(current_kikdb)
        #list_tags.reverse()
        table = BeautifulTable() #for pretty command line output
        #three_days_ago=datetime.datetime.now() - datetime.timedelta(days=recent_days)

        for row in list_tags:

            date_string=format_date(row[1],recent_days=3,short_date_format=short_date_format,         long_date_format=long_date_format)

            if not os.path.isfile(row[2]):
                pass#print(row[2], ' does not exist')
            #figure relative paths - inconsistent, abort!

            if '..' in row[2]:
                print(row[2], ' is a relative path')



            #print(row[2].split('/')[-1])
            ############################
            ####### FOR THIS TAG #######
            ############################
            # if searching for a tag return its modification date
            # if the sought filename was found
            if row[2] == filename or len(filename)==0: # comparing absolute paths in case a filename was provided
                if len(search_string)==0:
                    #table.append_row([row[0],date_string])
                    table.rows.append([row[0],date_string])
                    # TODO
                    #  'BeautifulTable.append_row' has been deprecated in 'v1.0.0' and will be removed in 'v1.2.0'. Use 'BTRowCollection.append' instead. 
                else:
                    if row[0]==search_string:
                        #table.append_row([row[0],date_string])
                        table.rows.append([row[0],date_string])
                        # TODO
                        #  'BeautifulTable.append_row' has been deprecated in 'v1.0.0' and will be removed in 'v1.2.0'. Use 'BTRowCollection.append' instead.
                        print(table)
                        return row[1]

        # ended looping on the tags contained in the file
        if not short_listing and len(search_string)==0:
            print(table)


        if len(search_string)==0:
            p_Table=pd.DataFrame(table.rows)
            print(p_Table.info())
            try:
                return p_Table[0].unique()[::-1]
            except KeyError:
                return []
        if len(filename)>0:
            return list_tags


if __name__ == '__main__':
    main(sys.argv[1:])
