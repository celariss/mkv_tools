__author__      = "Jérôme Cuq"

import subprocess, sys, os, json

def exit_script(value: int = 1):
    #log('exiting...')
    exit(1)


def log(message: str):
    print(message)


def log_error(message: str, exitScript: bool = False):
    """print an error and stop current script

    :param message: message to print out
    :type message: str
    :param exitScript: indicates whether the function must call exit, defaults to True
    :type exitScript: bool, optional
    """
    print("ERROR: "+message, file=sys.stderr)
    if exitScript:
        exit_script()

def filename_no_ext(file_path: str) -> str:
    """get the filename without extension from a file path

    :param file_path: path to the file
    :type file_path: str
    :return: filename without extension
    :rtype: str
    """
    return os.path.splitext(os.path.basename(file_path))[0]

def filepath_no_ext(file_path: str) -> str:
    """get the file path without extension from a file path

    :param file_path: path to the file
    :type file_path: str
    :return: file path without extension
    :rtype: str
    """
    return os.path.join(os.path.dirname(file_path), os.path.splitext(os.path.basename(file_path))[0])
		
def find_files(folder: str, extensions: list) -> list:
    """
    Recursively find all files in the given folder with specified extensions.

    :param folder: The root folder to start searching from.
    :param extensions: A list of file extensions to look for (e.g., ['.srt', '.sub']).
    :return: A list of paths to files found.
    """
    if not os.path.exists(folder):
         log_error("Folder <"+folder+"> does not exist", True)
         return

    res_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if any(file.lower().endswith(ext.lower()) for ext in extensions):
                res_files.append(os.path.join(root, file))
    return res_files

def call_process(args:list) -> str:
    try:
        return subprocess.check_output(args).decode()
    except FileNotFoundError as exc:
        filename = exc.filename
        if not filename:
            filename = args[0]
        log_error(str(exc) + " : '"+filename+"'",True)

def find_subtitles(path, codecs = []) -> dict:
    result = {}
    if not os.path.exists(path):
         log_error("Path <"+path+"> does not exist", True)
         return
    elif os.path.isfile(path):
        log("Reading subtitles in mkv file : "+path)
        tracks = find_subtitles_in_file(path, codecs)
        if len(tracks)>0:
            result[path] = tracks
    else:
        log("Gathering subtitles in mkv files from folder : "+path)
        mkv_files = find_files(path, ['.mkv'])
        for mkv in mkv_files:
            tracks = find_subtitles_in_file(mkv, codecs)
            if len(tracks)>0:
                result[mkv] = tracks
    return result

def find_subtitles_in_file(mkvfile, codecs = []) -> list:
    """
    Find all subtitles in mkvfile matching "codecs"
    
    "mkvmerge" binary must be installed and accessible
    => install mkvtoolnix package
    => ubuntu : sudo apt-get install mkvtoolnix
    
    :param mkvfile: path to mkv file
    :param codecs: list of codecs to match (as expressed in "codec" field of each track returned by "mkvmerge -J")
    :return: list of tracks as returned by mkvmerge
    :rtype: list
    """
    result = []
    info_json = json.loads(call_process(['mkvmerge', '-J', mkvfile]))
    if info_json['container']['recognized'] == True and info_json['container']['supported'] == True:
        for track in info_json['tracks']:
            if track['type'] == 'subtitles':
                codec = track['codec']
                if len(codecs)==0 or codec in codecs:
                    result.append(track)
    else:
        log_error('file <'+mkvfile+'> is not a recognized/supported mkv file !')
    return result
