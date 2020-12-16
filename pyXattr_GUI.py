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
from termcolor import colored
from pathlib import Path

print(colored("Tk version: "+str(TkVersion),'cyan'))


#short_date_format='%Y-%m-%d'
#long_date_format='%Y-%m-%d %H:%M'
#recent_days=3
def load_configuration(json_data,DEBUG=False):
    the_dict=load_current_json_as_dict(json_data)
    globals().update(the_dict)
    if DEBUG:
      print(colored(  "loaded settings from file:" ,'red'))
      print(colored(the_dict,'red') )
    return the_dict

settings=load_configuration('config.json')
PDFfolders=settings["PDFfolders"] # it reads one char at a time
#PDFfolders=["/Users/roberto/cernbox/BibDeskPDFs/"] #,'\"/Users/roberto/OneDrive - Universita degli Studi Roma Tre/Bibdesk2020\"']
for _d in PDFfolders:
  print(colored(_d,'green'))


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
  if len(value) <= 3:
      data = kwargs['list']
  else:
      data = []
      indexes=[]
      for _i_,item in enumerate(kwargs['list']):
          # Unix shell-style wildcards (which are not the same as regular expressions!)
          # https://docs.python.org/3/library/fnmatch.html
          if kwargs['method']=='unix':
              if len(fnmatch.filter([item.lower()],value.lower()))>0 :
                  # search Pattern
                  data.append(item)
                  indexes.append(_i_)
          if kwargs['method']=='re':
              import re
              reg_exp=value
              m = re.search(reg_exp, item.lower())
              if m is not None:
                  # search Pattern
                  data.append(item)
                  indexes.append(_i_)
  return indexes  
  # update data in listbox
  # listbox_update(kwargs['listbox'],data)
  # global_status_data=data


def listbox_update(_listbox,data,manipulation=None):
    # delete previous data
    _listbox.delete(0, 'end')

    # sorting data
    #data = sorted(data, key=str.lower)

    # put new data
    for item in data:
        if manipulation is None:
          _listbox.insert('end', item )
        else:
          if manipulation=='filename':
            print(colored('doing the manipulation','red'))
            _listbox.insert('end', Path(item).name )
          else:
            _listbox.insert('end', manipulation(item) )


def _listbox_update(_listbox,data):
    _listbox.config(listvariable=data)


def on_select(event,**kwargs):
    # display element selected on list
    current_selection_list = event.widget.curselection()
    current_selection_text = event.widget.get(event.widget.curselection())
 

    print('(event) previous:', event.widget.get('active'))
    if kwargs['object']=='file':
        print('(event)  current:', current_selection_text,' position: ',current_selection_list[0])
        print('---')
        current_files_kiks=pyXattr.main(['-l','-f',current_selection_text])
        if current_files_kiks is None:
            current_files_kiks=[]
        print('current_files_kiks(',len(current_files_kiks),'):',current_files_kiks)
        file_tags.set(tuple(current_files_kiks))
        search_results_list=current_files_kiks
    if kwargs['object']=='tag':
        modification_date=pyXattr.main(['-l','--search',current_selection_text ])
        print('modification_date:',modification_date)
        print('---')
        tag_date.set(format_date(modification_date,recent_days=recent_days,short_date_format=short_date_format, long_date_format=long_date_format) )


def populate_file_list(PDFfolders:list,ascending=False,listbox=None,DEBUG=True,manipulation=None):
    if DEBUG:
      print('PDFfolders ', PDFfolders,' type:', type(PDFfolders))
    list_of_fullpaths=list_folders(PDFfolders,ascending=ascending,fullpath=True)
    listbox_update(listbox,list_of_fullpaths,manipulation=manipulation)
    return list_of_fullpaths

def add():
    pass

# --- main ---

#keywords = ['Water Mellon','apple', 'banana', 'Cranberry', 'dogwood', 'alpha', 'Acorn', 'Anise', 'Strawberry' ]

keywords=pyXattr.main(['-l','-s'])

root = Tk()
root.title("Knowledge In Keywords `kik` Management")
root.option_add('*tearOff', FALSE)

ascending_sort_order=BooleanVar()
#ascending_sort_order = False
#print(keywords)




content = ttk.Frame(root)
mainframe = ttk.Frame(content,borderwidth=5, relief="sunken")#, width=1200, height=400)
#root.columnconfigure(0, weight=1)
#root.rowconfigure(0, weight=1)

search_method = StringVar()
search_method = 're'

##########################################
####### Variables sought in methods ######
##########################################
tag_date = StringVar()
file_tags = StringVar()
search_results_list = []


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
menu_edit.add_separator()
menu_edit.add_checkbutton(label='Ascending/Descending File Sorting', variable=ascending_sort_order, onvalue=True, offvalue=False)
menubar.add_cascade(menu=menu_search, label='SearchOptions')
menubar.add_cascade(menu=menu_help, label='Help')
menu_search.add_separator()
menu_search.add_checkbutton(label='Unix/Regular Expression', variable=search_method, onvalue='unix', offvalue='re')
#root.createcommand('tk::mac::ShowHelp', ...)
#menu_search.add_radiobutton(label='Unix', variable=search_method, value='unix')
#menu_search.add_radiobutton(label='Regular Expression', variable=search_method, value='re')

#####################
#      LABELS
#####################

search_style_label = ttk.Label(content, text='Search style:')
search_method_label = ttk.Label(content, text='Please select the type of search from the menu')
search_method_label['textvariable'] = search_method

ascending_sort_order_label = ttk.Label(content, text='Please select the type of sorting from the menu')
ascending_sort_order_label['textvariable'] = ascending_sort_order

output_date = ttk.Label(content, text='Date of last modification')
output_date['textvariable'] = tag_date

output_tags = ttk.Label(content, text='Current tags')
#output_tags.configure(text="%s%% completed" % percent)
output_tags['textvariable'] =  file_tags

#####################
#    HELP ELEMENT
#####################


from bs4 import BeautifulSoup
import cssutils
from tk_html_widgets import HTMLLabel, HTMLScrolledText

# get a HTML string from file
#############################
help_doc="GUI_HELP.html"  #from head to the end
help_doc_filehandle = open(help_doc, "r")
soup = BeautifulSoup(help_doc_filehandle, 'html.parser')
print(soup)
#############################

# get a dictionary form the CSS string in HTML string
#############################
style_string = soup.style.decode_contents()
style_dictionary = {}
sheet = cssutils.parseString(style_string)
for rule in sheet:
    selector = rule.selectorText
    styles = rule.style.cssText
    style_dictionary[selector] = styles
#############################

# get styled HTML from original HTML string
#############################
styled_html=soup.body.decode_contents()
for key,value in style_dictionary.items():
  old="class=\""+key.replace(".","")+"\""
  new="style=\""+value+";\""
  print( colored("DEBUG:",'red') , old , '->' , new )
  styled_html=styled_html.replace(old, new) 
#############################
  print(styled_html)

keyword_entry_help=HTMLScrolledText(content, 
  html=styled_html)
  #html='<li> <span style="background-color: LightGray;">*</span> matches everything,</li>')
  # html="<li><span style=\"background-color: LightGray;\">[!seq]</span> matches any character not in seq </li>")
  #html=soup.decode_contents())
keyword_entry_help.grid(column=0, row=0)
# .grid(column=0, row=0)  [](https://stackoverflow.com/questions/23584325/cannot-use-geometry-manager-pack-inside)

#fill="both", expand=True)
#keyword_entry_help.fit_height()


####################
###  TAGS LIST  ####
####################

#tagframe = LabelFrame(content, text="Tags")
#tagframe.pack(fill="both", expand="yes")

listbox_keywords = Listbox(content,width=30,height=100)
listbox_keywords.grid(column=0, row=0)
##listbox_keywords.bind('<Double-Button-1>', on_select)
#listbox_keywords.bind('<<ListboxSelect>>', on_select)
listbox_keywords.bind('<<ListboxSelect>>', functools.partial(on_select,object='tag'))
listbox_update(listbox_keywords,keywords)

key_word = StringVar()

keyword_entry = ttk.Entry(content,width=30,textvariable=key_word)
keyword_entry.grid(column=0, row=0)
keyword_entry.bind('<KeyRelease>', functools.partial(on_keyrelease,**{'listbox':listbox_keywords,'list':keywords,'method':search_method}) )
#SearchResultsTitleLabel=HTMLLabel(content, html='''<h1>Search Results</h1>''')



#filesframe = LabelFrame(content, text="Files")
#filesframe.pack(fill="both", expand="yes")

#scrollbar = Scrollbar(content)
#scrollbar.pack(side=RIGHT, fill=Y)
#ttk.Button(mainframe, text="Add", command=add).grid(column=2, row=2, sticky=W)

##listbox.bind('<Double-Button-1>', on_select)
#listbox_filenames.config(yscrollcommand=scrollbar.set)
#scrollbar.config(command=listbox_filenames.yview)
#populate_file_list(PDFfolders,ascending=ascending_sort_order,listbox=listbox_filenames,manipulation="filename" )



####################
###  FILE LIST  ####
####################


##### listbox_filenames = Listbox(content,width=80,height=100)#,yscrollcommand=scrollbar.set)
#####listbox_filenames.grid(column=0, row=0)
##### listbox_filenames.bind('<<ListboxSelect>>', functools.partial(on_select,listbox=listbox_filenames,object='file'))


##### file_name = StringVar()

##### filename_entry = ttk.Entry(content,width=80,textvariable=file_name)
##### filename_entry.grid(column=0, row=0)
##### filename_entry.bind('<KeyRelease>', functools.partial(on_keyrelease,listbox=listbox_filenames,\
#####      list=populate_file_list(PDFfolders,ascending=ascending_sort_order,listbox=listbox_filenames,manipulation=lambda x: Path(x).name )\
#####        ,method=search_method))
##### filename_entry.bind('<KeyRelease>', functools.partial(on_keyrelease,listbox=listbox_filenames,\
#####      list=populate_file_list(PDFfolders,ascending=ascending_sort_order,listbox=listbox_filenames,manipulation=lambda x: Path(x).name )\
#####        ,method=search_method))


#########################
###  NEW FILE LIST   ####
#########################
# obtain the two lists paths,filenames


def filter_list(value,method,list_):
  data = []
  indexes=[]
  for _i_,item in enumerate(list_):
      
      # Unix shell-style wildcards (which are not the same as regular expressions!)
      # https://docs.python.org/3/library/fnmatch.html
      if method=='unix':
        print(item)
        import fnmatch
        if len(fnmatch.filter([item.lower()],value.lower()))>0 :
            # search Pattern
            data.append(item)
            indexes.append(_i_)
      if method=='re':
        import re
        reg_exp=value
        m = re.search(reg_exp, item.lower())
        if m is not None:
          # search Pattern
          data.append(item)
          indexes.append(_i_)
  return indexes,data


def fetch_paths_fnames():
  orig_paths = list_folders(PDFfolders,ascending=ascending_sort_order,fullpath=True)
  orig_fnames = [  Path(p).name for p in orig_paths ]
  return orig_paths, orig_fnames

def reset_file_list():
  global current_paths
  global current_fnames
  current_paths ,  current_fnames = fetch_paths_fnames() # should be global


_p , _f = fetch_paths_fnames()

current_paths = _p
current_fnames = _f

def update_files_list(current_fnames):
  listbox_filenames.delete(0, 'end')
  listbox_filenames.insert('end', *current_fnames )

def on_select_sync(event):
  current_selection_list = event.widget.curselection()
  current_selection_text = event.widget.get(event.widget.curselection())
  print( colored( current_fnames[current_selection_list[0]] , "blue") )
  print(  colored( current_paths[current_selection_list[0]] , "cyan") )

def on_keyrelease_sync(event,**kwargs):
  global current_fnames
  global current_paths

  #print(kwargs)
  # get text from entry
  value = event.widget.get()
  value = value.strip().lower()

  # get data from list
  if len(value) <= 3:
    print(colored('less than 4 chars, doing nothing','yellow'))
  else:
    print(colored('working on ','yellow'),colored(value,'red'))
    filtered_indexes, filtered_fnames = filter_list(value,kwargs['method'],current_fnames)
    current_paths = [ current_paths[i] for i in filtered_indexes]
    
    current_fnames = [ current_fnames[i] for i in filtered_indexes]
    update_files_list(current_fnames)


  if value=='':
    print(colored('returning to original list','green'))
    reset_file_list()
    update_files_list(current_fnames)


reset_file_list() # act on global current_paths , current_fnames 

listbox_filenames = Listbox(content,width=80,height=100)#,yscrollcommand=scrollbar.set)
listbox_filenames.grid(column=0, row=0)
listbox_filenames.bind('<<ListboxSelect>>', on_select_sync )
file_name = StringVar()

filename_entry = ttk.Entry(content,width=80,textvariable=file_name)
filename_entry.grid(column=0, row=0)
filename_entry.bind('<KeyRelease>', functools.partial(on_keyrelease_sync,**{'method':'re'}) )

update_files_list(current_fnames)



####################
##### Results  #####
####################
listbox_results = Listbox(content,width=80,height=50,listvariable=file_tags)
#listbox_update(listbox_results,search_results_list)
listbox_results.grid(column=0, row=0)

results_frame = LabelFrame(content, text="Tags for this file")
results_frame.grid(column=0, row=0)#.pack(expand="yes")
entry_results = Entry(results_frame,width=60,textvariable=file_tags)
entry_results.grid(column=0, row=0)
write_tags = ttk.Button(results_frame, text='Write Tags', command=None)
write_tags.grid(column=0, row=0)

##########################
# ASSEMBLY OF THE WINDOW #
##########################
content.grid(column=0, row=0)
mainframe.grid(column=0, row=0, columnspan=3, rowspan=6) # 3 columns 4 rows
# row 1 # display of variables
search_style_label.grid(column=1,row=1,sticky=E)
search_method_label.grid(column=2,row=1,sticky=W)
ascending_sort_order_label.grid(column=3,row=1,sticky=W)
# row 2
keyword_entry.grid(column=1,row=2)
filename_entry.grid(column=2,row=2)
# row 3
output_date.grid(column=1,row=3,sticky=N)
output_tags.grid(column=2,row=3,sticky=N)
# row 4&5&6
listbox_keywords.grid(column=1,row=4,rowspan=3)
listbox_filenames.grid(column=2,row=4,sticky=W,rowspan=3)
keyword_entry_help.grid(column=3,row=4,sticky=N,rowspan=1)
results_frame.grid(column=3,row=5)
listbox_results.grid(column=3,row=6,sticky=N,rowspan=1)

keyword_entry.focus()

root.mainloop()
