#!/usr/bin/env python3
__author__      = "Jérôme Cuq"

import argparse, sys
from helpers import *

_sub_types = {'ASS': 'SubStationAlpha', 'SRT': 'SubRip/SRT'}

def build_track_order(replaced_track_id:list = [], new_track_id:list = [])->str:
    """ build the string that contains the track order to fill the --track-order parameter of mkvmerge.
    In the command line to be sent to mkvmerge :
      1) --subtitle-tracks or other --xxx-tracks parameter must be used for all tracks in "replaced_track_id"
      2) The new track files must be put after the files that replace tracks
    
    replaced_track_id: list of track ids (index) in source file that are to be replaced in target file.
    new_track_id: List of track ids (index)
    """
    result = []
    src_track_id = 0 # current track id in source mkv
    track_file_id = 0 # current index of external track file (ie also in replaced_track_id list)
    if len(replaced_track_id)>0:
        first_id = replaced_track_id[0]
        last_id = replaced_track_id[len(replaced_track_id)-1]
        # adding all source tracks that come before first replaced track
        for id in range(0, first_id):
            result.append('0:'+str(id))
        src_track_id = first_id
        # adding external tracks
        target_track_id = first_id # current track id in target mkv
        while track_file_id < len(replaced_track_id):
            # adding next track file in replaced_track_id
            result.append(str(track_file_id+1)+':0')
            track_file_id += 1
            target_track_id += 1
            #src_track_id += 1 # we have to jump other this track in src file
            # adding source tracks until next track in replaced_track_id, if any
            if track_file_id < len(replaced_track_id):
                for id in range(src_track_id, replaced_track_id[track_file_id]-track_file_id):
                    result.append('0:'+str(id))
                src_track_id = replaced_track_id[track_file_id]
                
    if len(new_track_id)>0:
        for id in new_track_id:
            while id>len(result):
                result.insert(id, '0:'+str(src_track_id))
                src_track_id += 1
            result.insert(id, str(track_file_id+1)+':0')
            track_file_id += 1
    
    if len(result)>0:
        return ','.join(result)
    return '0:0'


def convert_subtitles(path, in_codecs = [], out_type = 'SRT', save_src_files:bool = True):
    """
    Docstring for convert_subtitles
     "mkvmerge" and "ffmpeg" binaries must be installed and accessible
    
    :param path: path to an individual mkv file of to a folder
    :param in_codecs: list of codecs to match (as expressed in "codec" field of each track returned by "mkvmerge -J")
    :param out_type: type (from _sub_types) to convert tracks to
    :param save_src_files: Description
    :type save_src_files: bool
    """
    if not out_type in _sub_types:
        log_error('invalid output subtitle type given : '+out_type, True)

    subtracks = find_subtitles(path, in_codecs)

    if len(subtracks) == 0:
        log('no subtitle track found, nothing to do !')
        return

    for mkv in subtracks:
        log('processing '+str(len(subtracks[mkv]))+' track(s) in : ' + mkv)
        target_folder = os.path.dirname(mkv)

        log('   1) extracting and converting subtitles tracks')
        ffmpeg_params = ['ffmpeg', '-y', '-loglevel', 'error', '-i', mkv]
        for track in subtracks[mkv]:
            trackid = str(track['id'])
            out_file = filename_no_ext(mkv)+'-'+trackid+'.'+out_type.lower()
            ffmpeg_params.extend(['-map', '0:'+trackid+'?', os.path.join(target_folder,out_file)])
        call_process(ffmpeg_params)

        log('   2) building output mkv file')
        input_mkv = filepath_no_ext(mkv)+'_.mkv'
        tracks_to_remove = []
        tracks_to_add_params = []
        for track in subtracks[mkv]:
            tracks_to_remove.append(str(track['id']))
            trackid = str(track['id'])
            forced_flag = 'yes' if track['properties']['forced_track']==True else 'no'
            default_flag = 'yes' if track['properties']['default_track']==True else 'no'
            sub_file = filename_no_ext(mkv)+'-'+trackid+'.'+out_type.lower()
            if not 'track_name' in track['properties']:
                track['properties']['track_name'] = track['properties']['language']
            tracks_to_add_params.extend(['--language', '0:'+track['properties']['language'], '--track-name', '0:'+track['properties']['track_name'], '--forced-display-flag', '0:'+forced_flag, '--default-track-flag', '0:'+default_flag, os.path.join(target_folder,sub_file)])
        
        # Building track order to preserve original track order
        track_order = build_track_order(list(track['id'] for track in subtracks[mkv]))
        
        # Building mkvmerge command line
        mkvmerge_params = ['mkvmerge', '--quiet', '-o', mkv, '--track-order', track_order]
        # Adding parameters to remove subtitles tracks
        mkvmerge_params.extend(['--subtitle-tracks', '!'+','.join(tracks_to_remove)])
        # Adding input file path
        mkvmerge_params.append(input_mkv)
        # Adding parameters to add converted subtitles tracks
        mkvmerge_params.extend(tracks_to_add_params)

        # Let's go !
        os.rename(mkv, input_mkv)
        call_process(mkvmerge_params)
        if save_src_files:
            os.rename(input_mkv, filepath_no_ext(mkv)+'.bak')
        else:
            os.remove(input_mkv)
        for track in subtracks[mkv]:
            trackid = str(track['id'])
            sub_file = filepath_no_ext(mkv)+'-'+trackid+'.'+out_type.lower()
            os.remove(sub_file)


def main(argv):
    """
    dependencies :
    - mkvmerge
    - ffmpeg
    => ubuntu : sudo apt-get install mkvtoolnix ffmpeg
    """
    argParser = argparse.ArgumentParser(description="This script converts subtitles for a given mkv file, or for mkv files in a given folder, recursively")
    argParser.add_argument("path", help="path to mkv file or root folder to start the search from")
    argParser.add_argument("-i", "--in-type", help="type(s) of subtitles to find, among ['ASS','SRT']", nargs='+', metavar="input_type", dest="in_types")
    argParser.add_argument("-o", "--out-type", help="output subtitle type, among ['ASS','SRT']", required=True,metavar="output_type", dest="out_type")
    argParser.add_argument("-n", "--no-bak", help="if set, disable the saving of source files in file.bak", dest="no_bak", action="store_true")
    args = argParser.parse_args()

    path = args.path
    in_codecs = []
    if args.in_types:
        for t in args.in_types:
            if t.upper() in _sub_types.keys():
                in_codecs.append(_sub_types[t.upper()])
    out_type = args.out_type

    convert_subtitles(path, in_codecs, out_type.upper(), not args.no_bak)

    
if __name__ == "__main__":
   main(sys.argv[1:])