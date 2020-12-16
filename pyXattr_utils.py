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
from termcolor import colored

def DEBUG():
    return False
debugline="DEBUG: "

def load_current_json_as_dict(KikDeskFile):
    with open(KikDeskFile) as json_data:
        d = json.load(json_data)
        #print(d)
    return d
def load_current_json_kikdeskfile(KikDeskFile):
    return load_current_json_as_dict(KikDeskFile)



def serialize_dict_to_file_as_json(_emptydic,KikDeskFile):
    with open(KikDeskFile, "w") as outfile:
        json.dump(_emptydic, outfile)

def list_tags_in_reverse_time(current_kikdb):
    tags_times=[ [ [ tag["tag"], tag["time"], filekey ] for tag in get_tags_from_kik(kiks) ] for filekey, kiks in current_kikdb.items() ]
    flatlist=utils.flattenOnce(tags_times)
    _list=utils.sort_by_ith(flatlist,1)
    _df=pd.DataFrame(_list,columns=["tag", "time", "filekey"])
    return _list,_df



def format_date(row1,recent_days=3,short_date_format='%Y-%m-%d',\
long_date_format='%Y-%m-%d %H:%M'):
    three_days_ago=datetime.datetime.now() - datetime.timedelta(days=recent_days)

    d = datetime.datetime.fromtimestamp(float(row1))
    _date_format=short_date_format

    if d>three_days_ago:
        _date_format=long_date_format
    date_string = d.strftime(_date_format)

    return date_string


def get_tags_from_kik(kik_set):
    result=[]
    for element in kik_set:
        try:
            if len(element["tag"])>0:
                result.append(element)
        except KeyError:
            if DEBUG(): print( debugline, element, " was not a tag")
    return result

def get_bibitem_from_kik(kik_set):
    result=[]
    for element in kik_set:
        try:
            if len(element["bibitem"])>0:
                result=element["bibitem"]
        except KeyError:
            if DEBUG(): print( debugline, element, " was not a bibitem")
    return result


def check_if_tag_exists(initial_kik_set,tag):
    initial_tags_set=get_tags_from_kik(initial_kik_set)

    res=0
    for tt in range(len(initial_tags_set)):
        if initial_tags_set[tt]["tag"] == tag:
            res=1
            print( "tag ", tag, " already present. will not add it again")
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
        if DEBUG(): print( debugline, tags_array)
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
        if DEBUG(): print( debugline, tags_array)
        for tag in tags_array:
            clean_tag=utils.remove_multiple_spaces(tag)
            clean_tag=clean_tag.strip()
            if check_if_tag_exists(initial_tags_set,clean_tag)>0:
                print("... will remove it, instead.")
                working_tags_set = [ existing_tag for existing_tag in working_tags_set if clean_tag != existing_tag["tag"] ]

    if len(bibitem)>0:
        _this_tag={}
        _this_tag["bibitem"]=bibitem
        working_tags_set.append(_this_tag)
    return working_tags_set

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
            if DEBUG(): print( debugline, "current jpyXattr: ", son)
        else:
            print( "too many lines")
            sys.exit()
    except subprocess.CalledProcessError:
        son=[]

    return son


def list_folders(PDFfolders:list,ascending=False,DEBUG=True,fullpath=True,pandas_output=False,np_output=False):

    if isinstance(PDFfolders,list):
        dirlist=[]
        dir_df=pd.DataFrame()
        for PDFfolder in PDFfolders:
            if DEBUG:
                print(colored(PDFfolder,'green'))
            #dirlist = listdir_shell('/Users/roberto/cernbox/BibDeskPDFs/', ['-t'])
            #ls = subprocess.Popen(["ls", "-t", PDFfolder],                 stdout=subprocess.PIPE)
            #dirlist += [ (item.decode('UTF-8')).strip('\n') for item in ls.stdout ]
            files = os.listdir( str(PDFfolder) )
            #dirlist+=files
            ls_files = [ (PDFfolder+'/'+_file,_file,os.stat(PDFfolder+'/'+_file).st_mtime) for _file in files ]
            df_files = pd.DataFrame( ls_files    )
            print(df_files.info())
            dir_df=pd.concat([dir_df,df_files])

        dir_df.columns=['Path','filename','mtime']
        dir_df.sort_values(by='mtime',ascending=ascending,inplace=True)

        print(colored(dir_df.head(),'red'))

        print(dir_df.info())

        if fullpath:
            dirlist=dir_df.to_numpy()[:,0]
            return dirlist
        if pandas_output:
            return dir_df
        if np_output:
            _df_np=dir_df.to_numpy()
            return _df_np
           

    else:
        print(colored('the input of list_folders must be a list, not '+str(type(PDFfolders)),'red'))