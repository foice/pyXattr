#/usr/bin/env python
import time
import datetime
import json
import utils
import argparse
import subprocess
import sys

# manipulate a JSON list contained in the xattr ""
VERSION=0.1
def DEBUG():
    return False

debugline="DEBUG: "


def get_current_pyXattr(filename):
    #son=[]
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
                _this_tag["tag"]=tag
                _this_tag["mtime"]=human_time
                _this_tag["time"]=epoch_time
                working_tags_set.append(_this_tag)
                # add this tag to the registry ...
    return working_tags_set

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "-t", "--add_tag", default="", help="tags to be added. CSV format")
    parser.add_argument('-f', '--filename', default="test.pdf", help="file to be processed")
    args = parser.parse_args()
    ###################################
    filename=args.filename
    tags=args.add_tag
    ###################################


    #get the current tag value. it is a is a list of dictionaries
    initial_tags_set = get_current_pyXattr(filename)
    working_tags_set=extend_tags(initial_tags_set,tags)
    pyXtag=json.dumps(working_tags_set)

    if len(tags)>0:
        print "writing ", pyXtag
        res = subprocess.check_output(["xattr", "-w", "pyXattr", pyXtag, str(filename)])
        for line in res.splitlines():
            print line


if __name__ == '__main__':
    main()
