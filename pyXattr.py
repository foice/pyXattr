#/usr/bin/env python
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
VERSION=0.2
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
    tags_times=[ [ [ tag["tag"], tag["time"] ] for tag in tags ] for filekey, tags in current_kikdb.items() ]
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

def check_if_tag_exists(initial_tags_set,tag):
    res=0
    for tt in range(len(initial_tags_set)):
        if initial_tags_set[tt]["tag"] == tag:
            res=1
            print "tag ", tag, " already present. will not add it again"
    return res

def extend_tags(initial_tags_set,tags):
    working_tags_set = initial_tags_set;
    mod_time=datetime.datetime.now()
    human_time = mod_time.strftime("%A, %d. %B %Y %I:%M%p")
    epoch_time = mod_time.strftime("%s")
    if len(tags)>0:
        tags_array=tags.split(",")
        if DEBUG(): print debugline, tags_array
        for tag in tags_array:
            if check_if_tag_exists(initial_tags_set,tag)==0:
                _this_tag={}
                _this_tag["tag"]=remove_multiple_spaces(tag).strip
                _this_tag["mtime"]=human_time
                _this_tag["time"]=epoch_time
                working_tags_set.append(_this_tag)
                # add this tag to the registry ...
    return working_tags_set

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "-t", "--add_tag", default="", help="tags to be added. CSV format")
    parser.add_argument('-f', '--filename', default="", help="file to be processed")
    parser.add_argument('-l', '--list', default=False, action="store_true", help="list recently used tags putting most revent the bottom of the  list")
    args = parser.parse_args()
    ###################################
    filename=args.filename
    tags=args.add_tag
    listing=args.list
    ###################################

    if (len(filename)>0):
        #get the current tag value. it is a is a list of dictionaries
        initial_tags_set = get_current_pyXattr(filename)
    if len(tags)>0: # is the same as saying -a or -t or --add_tag was provided
        # extend the tags
        working_tags_set=extend_tags(initial_tags_set,tags)
        # make the tags into JSON
        pyXtag=json.dumps(working_tags_set)
        # write the tags
        print "writing ", pyXtag
        res = subprocess.check_output(["xattr", "-w", "pyXattr", pyXtag, str(filename)])
        for line in res.splitlines():
            print line

        # extend the kikDB
        kikdesk_file_exists=os.path.isfile(KikDeskFile)
        if not kikdesk_file_exists:
            _emptydic={}
            serialize_dict_to_file_as_json(_emptydic,KikDeskFile)

        current_kikdb=load_current_json_kikdeskfile(KikDeskFile)
        serialize_dict_to_file_as_json(current_kikdb,KikDeskFile+".back")

        print current_kikdb
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
