# mkv_tools
### A set of python scripts to manipulate mkv files

<p align="middle">
    <img src="doc/img/icon-default.png"/>
</p>

##

mkv_tools is a set of python script to manipulate mkv files
For now, it is only composed of 2 scripts :
- find_subtitles : find all subtitles of given type from a mkv file or a folder of mkv files
- convert_subtitles : convert subtitles of a mkv file or a folder of mkv files. Useful to get rid of corrupted ASS subtitles.

## find_subtitles
This script outputs subtitles tracks found in a given mkvfile or in all mkvfiles of a given folder.

#### install dependencies (for ubuntu) :
```sh
sudo apt-get install mkvtoolnix
```

#### to get usage info, use :
```sh
python3 find_subtitles.py -h
```

## convert_subtitles
This script converts subtitles tracks found in a given mkvfile or in all mkvfiles of a given folder.
Typically, it can be used to convert ASS subtitles to SRT.
It preserves subtitles orders and default/forced tags of all subtitles.

#### install dependencies (for ubuntu) :
```sh
sudo apt-get install mkvtoolnix ffmpeg
```

#### to get usage info, use :
```sh
python3 convert_subtitles.py -h
```

