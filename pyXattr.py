#/usr/bin/env python
import time
import datetime
import json
import utils
import argparse
import subprocess
#import optparse
# manipulate a JSON list contained in the xattr ""
VERSION=0.1



def main():
    parser = argparse.ArgumentParser()
    #parser.add_argument("-a", "--add_tag", help="increase output verbosity",
    #                    action="store_true")
    parser.add_argument("-a", "--add_tag", default="", help="tags to be added. CSV format")
    parser.add_argument('-f', '--filename', default="test.pdf", help="file to be processed")
    args = parser.parse_args()

    filename=args.filename
    tags=args.add_tag
    mod_time=datetime.datetime.now()

    human_time = mod_time.strftime("%A, %d. %B %Y %I:%M%p")
    epoch_time = mod_time.strftime("%s")
    #get the current tag value. it is a json

    res = subprocess.check_output(["xattr", "-p", "pyXattr", str(filename)])
    for line in res.splitlines():
        print "current pyXattr: ", line
        son = json.loads(line)
        print "current jpyXattr: ", son

    if son is  "No such xattr: pyXtag":
        tags_set=[]
    else:
        tags_set=son
        print "initial tags: ", tags_set
        print tags_set[0]["tag"]

            
    tags_array=tags.split(",")
    for tag in tags_array:
        _this_tag={}
        _this_tag["tag"]=tag
        _this_tag["mtime"]=human_time
        _this_tag["time"]=epoch_time
        tags_set.append(_this_tag)

    pyXtag=json.dumps(tags_set)
    print "writing ", pyXtag
    res = subprocess.check_output(["xattr", "-w", "pyXattr", pyXtag, str(filename)])
    for line in res.splitlines():
        print line


if __name__ == '__main__':
    main()
