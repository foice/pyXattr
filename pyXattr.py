#!/usr/bin/env python

import time
import datetime, time
import json
import utils
import argparse
import subprocess
import sys, os
import utils
from beautifultable import BeautifulTable
# manipulate a JSON list contained in the xattr called pyXattr
# keep track of the same in a python dictionary serialized at $KikDeskFile

# TODO


VERSION=0.5
def DEBUG():
    return False
debugline="DEBUG: "

KikDeskFile="/Users/roberto/Dropbox/BibReader/Tags.kik"

#### output format and options ####
short_date_format='%Y-%m-%d'
long_date_format='%Y-%m-%d %H:%M'
recent_days=0.5

def load_current_json_kikdeskfile(KikDeskFile):
    with open(KikDeskFile) as json_data:
        d = json.load(json_data)
        #print(d)
    return d

def serialize_dict_to_file_as_json(_emptydic,KikDeskFile):
    with open(KikDeskFile, "w") as outfile:
        json.dump(_emptydic, outfile)

def list_tags_in_reverse_time(current_kikdb):
    tags_times=[ [ [ tag["tag"], tag["time"] ] for tag in get_tags_from_kik(kiks) ] for filekey, kiks in current_kikdb.items() ]
    faltlist=utils.flattenOnce(tags_times)
    return utils.sort_by_ith(faltlist,1)

def get_current_pyXattr(filename):
    son=[]
    try:
        res = subprocess.check_output(["xattr", "-p", "pyXattr", str(filename)])
        #res is stdout. it has 0 lines when the attribute is missing, because then we only have stderr
        lines=res.splitlines()
        if len(lines)==0:
            son=[]
        elif len(lines)==1:
            son = json.loads(lines[0])
            if DEBUG(): print debugline, "current jpyXattr: ", son
        else:
            print "too many lines"
            sys.exit()
    except subprocess.CalledProcessError:
        son=[]

    return son

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

def get_tags_from_kik(kik_set):
    result=[]
    for element in kik_set:
        try:
            if len(element["tag"])>0:
                result.append(element)
        except KeyError:
            if DEBUG(): print debugline, element, " was not a tag"
    return result

def get_bibitem_from_kik(kik_set):
    result=[]
    for element in kik_set:
        try:
            if len(element["bibitem"])>0:
                result=element["bibitem"]
        except KeyError:
            if DEBUG(): print debugline, element, " was not a bibitem"
    return result


def check_if_tag_exists(initial_kik_set,tag):
    initial_tags_set=get_tags_from_kik(initial_kik_set)

    res=0
    for tt in range(len(initial_tags_set)):
        if initial_tags_set[tt]["tag"] == tag:
            res=1
            print "tag ", tag, " already present. will not add it again"
    return res

def extend_tags(initial_kik_set,kik):

    initial_tags_set=get_tags_from_kik(initial_kik_set)
    initial_bibitem=get_bibitem_from_kik(initial_kik_set)

    #initial_tags_set must be split in the bibitem part and the rest
    tags=kik.tags
    _mtime=kik.mtime

    bibitem=""
    if len(kik.bibitem)>0:
        bibitem=kik.bibitem
    elif len(initial_bibitem)>0:
        bibitem=initial_bibitem

    working_tags_set = initial_tags_set;
    if _mtime=="":
        mod_time=datetime.datetime.now()
    else:
        mod_time = datetime.datetime.fromtimestamp(float(_mtime))

    human_time = mod_time.strftime("%A, %d. %B %Y %I:%M%p")
    epoch_time = mod_time.strftime("%s")
    if len(tags)>0:
        tags_array=tags.split(",")
        if DEBUG(): print debugline, tags_array
        for tag in tags_array:
            clean_tag=utils.remove_multiple_spaces(tag)
            clean_tag=clean_tag.strip()
            if check_if_tag_exists(initial_tags_set,clean_tag)==0:
                _this_tag={}
                _this_tag["tag"]=clean_tag
                _this_tag["mtime"]=human_time
                _this_tag["time"]=epoch_time
                working_tags_set.append(_this_tag)
                # add this tag to the registry ...
    if len(bibitem)>0:
        _this_tag={}
        _this_tag["bibitem"]=bibitem
        working_tags_set.append(_this_tag)

    return working_tags_set

def remove_tags(initial_kik_set,kik):
    initial_tags_set=get_tags_from_kik(initial_kik_set)
    initial_bibitem=get_bibitem_from_kik(initial_kik_set)

    tags=kik.tags

    bibitem=""
    if len(kik.bibitem)>0:
        bibitem=kik.bibitem
    elif len(initial_bibitem)>0:
        bibitem=initial_bibitem

    working_tags_set = initial_tags_set;
    mod_time=datetime.datetime.now()
    human_time = mod_time.strftime("%A, %d. %B %Y %I:%M%p")
    epoch_time = mod_time.strftime("%s")
    if len(tags)>0:
        tags_array=tags.split(",")
        if DEBUG(): print debugline, tags_array
        for tag in tags_array:
            clean_tag=utils.remove_multiple_spaces(tag)
            clean_tag=clean_tag.strip()
            if check_if_tag_exists(initial_tags_set,clean_tag)>0:
                print "... will remove it, instead."
                working_tags_set = [ existing_tag for existing_tag in working_tags_set if clean_tag != existing_tag["tag"] ]

    if len(bibitem)>0:
        _this_tag={}
        _this_tag["bibitem"]=bibitem
        working_tags_set.append(_this_tag)
    return working_tags_set


# TODO
# option to use this script that implies the same operation is done on OS X tags usings
# tag -a file
# tag -r file
# TODO
# add a function to change the keyword field of the bibtex file, possibly through BibDesk, which is likely to be concurrently using the file, hence better not pass above it.

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "-t", "--add_tag", default="", help="tags to be added. CSV format")
    parser.add_argument("-r", "--remove_tag", default="", help="tags to be removed. CSV format")
    parser.add_argument('--not_sync_osx', default=True, action="store_false", help="do not call tag utility to keep in sync the OS X tags (which are accessible in Finder and searchable via spotlight tag: )")
    parser.add_argument('-f', '--filename', default="", help="file to be processed")
    parser.add_argument("-b", "--bibitem", default="", help="bibitem string to be added as a tag")
    parser.add_argument("-m", "--mtime", default="", help="epoch time at which to place the time info of the tag")
    parser.add_argument('-l', '--list', default=False, action="store_true", help="list recently used tags putting most revent the bottom of the  list")
    args = parser.parse_args()
    ###################################
    filename=args.filename
    listing=args.list
    m_time=args.mtime
    bibitem=args.bibitem
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
        print "writing ", pyXtag
        res = subprocess.check_output(["xattr", "-w", "pyXattr", pyXtag, str(filename)])
        for line in res.splitlines():
            print line

        # update the kikDB, valid for both grow or shrink
        kikdesk_file_exists=os.path.isfile(KikDeskFile)
        if not kikdesk_file_exists:
            _emptydic={}
            serialize_dict_to_file_as_json(_emptydic,KikDeskFile)

        current_kikdb=load_current_json_kikdeskfile(KikDeskFile)
        serialize_dict_to_file_as_json(current_kikdb,KikDeskFile+".back")

        if DEBUG(): print current_kikdb
        new_kikdb=current_kikdb
        new_kikdb[str(filename)]=working_tags_set
        serialize_dict_to_file_as_json(new_kikdb,KikDeskFile)

    if listing:
        current_kikdb=load_current_json_kikdeskfile(KikDeskFile)
        list_tags=list_tags_in_reverse_time(current_kikdb)
        #list_tags.reverse()
        table = BeautifulTable()
        three_days_ago=datetime.datetime.now() - datetime.timedelta(days=recent_days)
        for row in list_tags:
            d = datetime.datetime.fromtimestamp(float(row[1]))
            _date_format=short_date_format

            if d>three_days_ago:
                _date_format=long_date_format
            date_string = d.strftime(_date_format)
            table.append_row([row[0],date_string])
        print(table)




if __name__ == '__main__':
    main()
