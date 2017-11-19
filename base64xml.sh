#!/bin/bash
# thanks to https://github.com/foice/BibDesk2Zotero_attachments
echo "$1" > path.encoded
base64 -D -i path.encoded -o path.dec
cp path.dec "$2".xml
plutil -convert xml1 "$2".xml
