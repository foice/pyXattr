#!/usr/bin/env python3.7

#import tkinter as tk
from tkinter import *
from tkinter import ttk
import pyXattr
import os
from subprocess import Popen, PIPE
import subprocess
import functools
import fnmatch

def listdir_shell(path, lsargs):
    list_command=['ls'] + lsargs + [path]
    print(list_command)
    p = Popen(list_command, shell=False, stdout=PIPE, close_fds=True)
    print(p.stdout.readlines()[:10])
    #os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    return p.stdout.readlines()
    #return [ str(path).rstrip('\n') for path in p.stdout.readlines()]

def on_keyrelease(event,**kwargs):

    #print(kwargs)
    # get text from entry
    value = event.widget.get()
    value = value.strip().lower()

    # get data from list
    if value == '':
        data = kwargs['list']
    else:
        data = []
        for item in kwargs['list']:
            #if value in item.lower(): # search for substring no regular expression or wildcards *
            if len(fnmatch.filter([item.lower()],value.lower()))>0 :
                # search Pattern
                data.append(item)

    # update data in listbox
    listbox_update(kwargs['listbox'],data)


def listbox_update(_listbox,data):
    # delete previous data
    _listbox.delete(0, 'end')

    # sorting data
    #data = sorted(data, key=str.lower)


    # put new data
    for item in data:
        _listbox.insert('end', item)


def on_select(event):
    # display element selected on list
    current_selection_text=event.widget.get(event.widget.curselection())
    print('(event) previous:', event.widget.get('active'))
    print('(event)  current:', current_selection_text)
    print('---')
    current_files_kiks=pyXattr.main(['-l','-f',PDFfolder+current_selection_text])
    print(current_files_kiks)

def add():
    pass
# --- main ---

#keywords = ['Water Mellon','apple', 'banana', 'Cranberry', 'dogwood', 'alpha', 'Acorn', 'Anise', 'Strawberry' ]

keywords=pyXattr.main(['-l','-s'])

#print(keywords)


PDFfolder="/Users/roberto/cernbox/BibDeskPDFs/"

#dirlist = listdir_shell('/Users/roberto/cernbox/BibDeskPDFs/', ['-t'])
ls = subprocess.Popen(["ls", "-t", PDFfolder],                 stdout=subprocess.PIPE)
dirlist = [ (item.decode('UTF-8')).strip('\n') for item in ls.stdout ]

#print(dirlist)

root = Tk()
root.title("Keywords Management")
content = ttk.Frame(root)

mainframe = ttk.Frame(content,borderwidth=5, relief="sunken")#, width=1200, height=400)
#root.columnconfigure(0, weight=1)
#root.rowconfigure(0, weight=1)



listbox_keywords = Listbox(content,width=30,height=100)
listbox_keywords.pack()
##listbox_keywords.bind('<Double-Button-1>', on_select)
listbox_keywords.bind('<<ListboxSelect>>', on_select)
listbox_update(listbox_keywords,keywords)

key_word = StringVar()

keyword_entry = ttk.Entry(content,width=30,textvariable=key_word)
keyword_entry.pack()
keyword_entry.bind('<KeyRelease>', functools.partial(on_keyrelease,**{'listbox':listbox_keywords,'list':keywords}) )

keyword_entry_help = ttk.Label(content, \
text=\
'* matches everything,  \
? matches any single character,  \
[seq] matches any character in seq,  \
[!seq] matches any character not in seq\n \
e.g. type "*Weinberg*" to search for anything containing "Weinberg"')

#ttk.Button(mainframe, text="Add", command=add).grid(column=2, row=2, sticky=W)
listbox_filenames = Listbox(content,width=80,height=100)
listbox_filenames.pack()
##listbox.bind('<Double-Button-1>', on_select)
listbox_filenames.bind('<<ListboxSelect>>', on_select)
listbox_update(listbox_filenames,dirlist)

file_name = StringVar()

filename_entry = ttk.Entry(content,width=80,textvariable=file_name)
filename_entry.pack()
filename_entry.bind('<KeyRelease>', functools.partial(on_keyrelease,listbox=listbox_filenames,list=dirlist))


content.grid(column=0, row=0)
mainframe.grid(column=0, row=0, columnspan=3, rowspan=3)
keyword_entry.grid(column=1,row=1)
keyword_entry_help.grid(column=1,row=2,columnspan=3)
listbox_keywords.grid(column=1,row=3)

filename_entry.grid(column=2,row=1)
listbox_filenames.grid(column=2,row=3)

#keyword_entry.focus()

root.mainloop()
