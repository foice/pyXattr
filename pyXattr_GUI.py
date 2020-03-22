#!/usr/bin/env python3.7

#import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkhtmlview import HTMLLabel
import pyXattr
import os
from subprocess import Popen, PIPE
import subprocess
import functools
import fnmatch
from pyXattr_utils import *

short_date_format='%Y-%m-%d'
long_date_format='%Y-%m-%d %H:%M'
recent_days=3

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
            # Unix shell-style wildcards (which are not the same as regular expressions!)
            # https://docs.python.org/3/library/fnmatch.html
            if kwargs['method']=='unix':
                if len(fnmatch.filter([item.lower()],value.lower()))>0 :
                    # search Pattern
                    data.append(item)
            if kwargs['method']=='re':
                import re
                reg_exp=value
                m = re.search(reg_exp, item.lower())
                if m is not None:
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


def on_select(event,**kwargs):
    # display element selected on list
    current_selection_text=event.widget.get(event.widget.curselection())
    print('(event) previous:', event.widget.get('active'))
    if kwargs['object']=='file':
        print('(event)  current:', current_selection_text)
        print('---')
        current_files_kiks=pyXattr.main(['-l','-f',PDFfolder+current_selection_text])
        print(current_files_kiks)
    if kwargs['object']=='tag':
        modification_date=pyXattr.main(['-l','--search',current_selection_text ])
        #print(modification_date)
        print('---')
        tag_date.set(format_date(modification_date,recent_days=recent_days,short_date_format=short_date_format,         long_date_format=long_date_format) )

def add():
    pass

# --- main ---

#keywords = ['Water Mellon','apple', 'banana', 'Cranberry', 'dogwood', 'alpha', 'Acorn', 'Anise', 'Strawberry' ]

keywords=pyXattr.main(['-l','-s'])

#print(keywords)

PDFfolders=["/Users/roberto/cernbox/BibDeskPDFs/","/Users/roberto/OneDrive - Universitá Degli Studi Roma Tre/Bibdesk2020"]

#PDFfolder="/Users/roberto/cernbox/BibDeskPDFs/"
dirlist=[]
for PDFfolder in PDFfolders:
    print(PDFfolder)
    #dirlist = listdir_shell('/Users/roberto/cernbox/BibDeskPDFs/', ['-t'])
    ls = subprocess.Popen(["ls", "-t", PDFfolder],                 stdout=subprocess.PIPE)
    dirlist += [ (item.decode('UTF-8')).strip('\n') for item in ls.stdout ]
    #print(dirlist)

root = Tk()
root.title("Knowledge In Keywords `kik` Management")
root.option_add('*tearOff', FALSE)

content = ttk.Frame(root)
mainframe = ttk.Frame(content,borderwidth=5, relief="sunken")#, width=1200, height=400)
#root.columnconfigure(0, weight=1)
#root.rowconfigure(0, weight=1)

search_method = StringVar()
tag_date = StringVar()

search_method = 're'
win = Toplevel(root)
menubar = Menu(win)
appmenu = Menu(menubar, name='apple')
menubar.add_cascade(menu=appmenu)
appmenu.add_command(label='About My Application')
appmenu.add_separator()
#
win['menu'] = menubar
#menubar = Menu(root)
# The menu's
menu_file = Menu(menubar)
menu_edit = Menu(menubar)
menu_search = Menu(menubar)
menu_help = Menu(menubar)

menubar.add_cascade(menu=menu_file, label='File')
menubar.add_cascade(menu=menu_edit, label='Edit')
menubar.add_cascade(menu=menu_search, label='SearchOptions')
menubar.add_cascade(menu=menu_help, label='Help')
menu_search.add_separator()
menu_search.add_checkbutton(label='Unix/Regular Expression', variable=search_method, onvalue='unix', offvalue='re')
#root.createcommand('tk::mac::ShowHelp', ...)
#menu_search.add_radiobutton(label='Unix', variable=search_method, value='unix')
#menu_search.add_radiobutton(label='Regular Expression', variable=search_method, value='re')

search_style_label = ttk.Label(content, text='Search style:')
search_method_label = ttk.Label(content, text='Please select the type of search from the menu')
search_method_label['textvariable'] = search_method

output_date = ttk.Label(content, text='Date of last modification')
output_date['textvariable'] = tag_date
####################
###  TAGS LIST  ####
####################
listbox_keywords = Listbox(content,width=30,height=100)
listbox_keywords.pack()
##listbox_keywords.bind('<Double-Button-1>', on_select)
#listbox_keywords.bind('<<ListboxSelect>>', on_select)
listbox_keywords.bind('<<ListboxSelect>>', functools.partial(on_select,object='tag'))
listbox_update(listbox_keywords,keywords)

key_word = StringVar()

keyword_entry = ttk.Entry(content,width=30,textvariable=key_word)
keyword_entry.pack()
keyword_entry.bind('<KeyRelease>', functools.partial(on_keyrelease,**{'listbox':listbox_keywords,'list':keywords,'method':search_method}) )


keyword_entry_help=HTMLLabel(content, html='''
      <head>
    <style>

.code {
  background-color: LightGray;
}

body {
  background-color: linen;
}

h1 {
  color: maroon;
  margin-left: 40px;
}
</style> <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title></title>
  </head>
  <body>
    <h1>Search syntax</h1>
    <h3> Unix-style: </h3>
    <ul>
      <li> <span class="code">*</span> matches everything,</li>
      <li><span class="code">[seq] </span> matches any
        character in seq</li>
      <li><span class="code">[!seq]</span> matches any character not in seq </li>
    </ul>
    <ul>
      e.g. type <span class="code">*Weinberg*</span> to search for anything containing "Weinberg"
    </ul>
    <p></p>
    <h3> Regulars expressions:</h3>
    <p><a href="https://docs.python.org/3/library/re.html#module-re">
        https://docs.python.org/3/library/re.html\#module-re&nbsp;</a></p>
    <ul>
      For example, <span class="code">Isaac (?!Asimov)</span> will match "Isaac " only if it is not
      followed by "Asimov".
    </ul>
    <h1> Tags Notation:</h1>
    <ul>
      <li>The names starting with G: are names of Bibdesk static groups. They
        can have been created issuing <span class="code">./bibgroups2keywords.py -b myfile.bib -k
        -a</span> </li>
    </ul>
''')

####################
###  FILE LIST  ####
####################

#ttk.Button(mainframe, text="Add", command=add).grid(column=2, row=2, sticky=W)
listbox_filenames = Listbox(content,width=80,height=100)
listbox_filenames.pack()
##listbox.bind('<Double-Button-1>', on_select)
listbox_filenames.bind('<<ListboxSelect>>', on_select)
listbox_update(listbox_filenames,dirlist)

file_name = StringVar()

filename_entry = ttk.Entry(content,width=80,textvariable=file_name)
filename_entry.pack()
filename_entry.bind('<KeyRelease>', functools.partial(on_keyrelease,listbox=listbox_filenames,list=dirlist,method=search_method))


##########################
# ASSEMBLY OF THE WINDOW #
##########################
content.grid(column=0, row=0)
mainframe.grid(column=0, row=0, columnspan=3, rowspan=5) # 3 columns 4 rows
# row 1
search_style_label.grid(column=1,row=1,sticky=E)
search_method_label.grid(column=2,row=1,sticky=W)
# row 2
keyword_entry.grid(column=1,row=2)
filename_entry.grid(column=2,row=2)
# row 3
output_date.grid(column=1,row=3,sticky=N)
# row 4&5
listbox_keywords.grid(column=1,row=4,rowspan=2)
listbox_filenames.grid(column=2,row=4,sticky=W,rowspan=2)
keyword_entry_help.grid(column=3,row=4,sticky=N,rowspan=1)

keyword_entry.focus()

root.mainloop()
