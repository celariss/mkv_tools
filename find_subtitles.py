#!/usr/bin/env python3
__author__      = "Jérôme Cuq"

import argparse, sys
from helpers import *

_sub_types = {'ASS': 'SubStationAlpha', 'SRT': 'SubRip/SRT'}


def main(argv):
    """
    dependencies :
    - mkvtoolnix package
      => ubuntu : sudo apt-get install mkvtoolnix
    """
    argParser = argparse.ArgumentParser(description="This script searches for mkv files that contain subtitles in a given folder, recursively")
    argParser.add_argument("path", help="path to mkv file or root folder to start the search from")
    argParser.add_argument("-t", "--sub_type", help="type of subtitles to find, in ['ASS','SRT']", nargs='*', metavar="sub_type", dest="sub_types")
    args = argParser.parse_args()

    path = args.path
    codecs = []
    if args.sub_types:
        for t in args.sub_types:
            if t.upper() in _sub_types.keys():
                codecs.append(_sub_types[t.upper()])
            else:
                log_error('invalid output subtitle type given : '+t, True)

    subtracks = find_subtitles(path, codecs)

    for mkv in subtracks:
        for track in subtracks[mkv]:
            log(mkv+': (#'+str(track['properties']['number'])+', '+track['codec']+')')

if __name__ == "__main__":
   main(sys.argv[1:])