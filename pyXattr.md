# What is `pyXttr`

`pyXattr` is a manager for `keywords` associated to your files. These keywords are helpful handles to retrieve your files. The keywords are stored in a JSON file and can be optionally written as Mac OS X `tags` or `extended attributes`

The JSON follows the format:
```
{ "full path": [{"tag": "tagname", "time": "epochtime", "mtime": "ascii modificatoin time"}]}
```

To access extended attributes `pyXattr` uses on `xattr` and is mainly tested with the 0.6.4 python2 version of xattr [BSD version of 2010](./xattr.man) shipped with Mac OS X 10.15 in `/System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/xattr/`

Ta access tags it uses OS X shell utility `tag` (usually found at `/usr/local/bin/tag`). Tags can be searched via `Spotlight`. Special tags `blue`, `orange`, `red`, `yellow`, `green`, `purple` are visible as colored tags in `Finder`.


## Features in v0
- from a single file: 
    - using `xattr` read and print the tags of the specificed file 
        ```
        pyXattr.py -l -f <file>
        ```


- manage a `.kik` file (in JSON format)
    - list all tags from the `.kik` file in chronological order
        ```
        pyXattr.py -l 
        TODO: alphabetical order
        ```
    - list all matching *exactly* a tag from the `.kik` file in chronological order 
        ```
        pyXattr.py -l --search "Non equilibrium"
        TODO: alphabetical order
        ```
    - write a new tag extending previous tags for a single file
        ```
        pyXattr.py -a <tag> -f <file>
        ```
    - remove a tag while keeping previous tags for a single file
        ```
        pyXattr.py -r <tag> -f <file>
        ```
## Features in v1
- use `xattr` to manage keywords directly on the file 
- use `tag` to manage tags directyl on the file


