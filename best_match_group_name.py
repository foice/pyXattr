#!/usr/bin/env python
import utils
import argparse
import math


VERSION=0.1
def DEBUG():
    return False
debugline="DEBUG: "


# https://stackoverflow.com/questions/36013295/find-best-substring-match
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--group_name", default="", help="string to search into")
    parser.add_argument("-q", "--query", default="", help="string to query")
    parser.add_argument("-c", "--csv", default="", help="CSV string to search into")

    args = parser.parse_args()
    ###################################
    group_name=args.group_name
    query=args.query
    csv=args.csv

    _step=len(query.split(' '))
    # print ' '.split(query)
    # print query.split(' ')
    _flex=int(math.floor(_step/2))

    if len(group_name)>0:
        #print "running with floor", _flex, "step",_step
        match=utils.get_best_match(query, group_name, step=1, flex=0, case_sensitive=False, verbose=False)
        print list(match)

    best_matches=[]
    if len(csv)>0:
        #print csv
        csv_group_names=utils.read_file_to_lines(csv)
        _line=csv_group_names[0].strip()
        # print _line
        #utils.write_lines_to_file_newline(csv,'/Users/roberto/filename_groups')
        group_names=_line.split(",")
        #print group_names
        # utils.write_lines_to_file_newline(group_names,'/Users/roberto/filename_groups_CSV')
        for _group_name in group_names:
            #print _group_name
            try:
                short=query
                longs=_group_name
                if (len(short)>len(longs)):
                    longs=query
                    short=_group_name
                _match=utils.get_best_match(short, longs, step=1, flex=0, case_sensitive=False, verbose=False)
                result=list(_match)
                result.append(_group_name)
                best_matches.append(result)
                #print _match
            except ValueError:
                print _group_name, " gives an error!"

        sorted_best_matches=utils.sort_by_ith(best_matches,1)
        #print sorted_best_matches
        _best_score=sorted_best_matches[-1][1]
        #print _best_score
        sorted_best_matches_head = [ item[2] for item in sorted_best_matches if _best_score == item[1] ]
        print sorted_best_matches_head

if __name__ == '__main__':
    main()
