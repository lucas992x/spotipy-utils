This repository contains various Python scripts that interact with Spotify using [Spotipy](https://spotipy.readthedocs.io/).

# Setup
Create an app at [Developers Dashboard](https://developer.spotify.com/dashboard/), take note of **Client ID** and **Client Secret**, set a **Redirect URI**: it does not need to be an actual website, you can use for example `http://localhost:8888/callback` or `http://localhost/`. Once everything is set up you need to save them as environment variables: the easiest way is to add the following lines in ~/.bash_aliases or wherever you put custom aliases (on Windows replace `export` with `SET`).
```
export SPOTIPY_CLIENT_ID='<Client ID>'
export SPOTIPY_CLIENT_SECRET='<Client Secret>'
export SPOTIPY_REDIRECT_URI='<Redirect URI>'
```
Then take note of your Spotify username: it is the one seen in profile URL (`https://open.spotify.com/user/<username>`) because displayed name may be different.

## Dependencies
- [spotipy](https://spotipy.readthedocs.io/)
- [pandas](https://pandas.pydata.org/)

# Scripts
`tools.py` contains various utility functions and is not meant to be executed standalone, other scripts are listed below in alphabetical order. Here are common arguments:
- `--user`: Spotify username (explained above), needed unless otherwise specified.
- `--auth`: authentication mode, by default is "auto", but can be set to "manual" when opening browser has issues or is not possible at all (e.g. in CLI-only environments).

All `.txt` files used as input by scripts should be placed in script's directory and contain in each row a playlist id and, optionally, additional text (e.g. playlist name) separated by space; the same format is used by `list-user-playlists.py`'s output, so it's easier to run it and pick needed playlists rather than getting ids one by one from Spotify. Examples are included in this repository.

## `export-playlists.py`
This script exports all playlists of given user. Arguments:
- `--dir` (_optional_): path of directory where files will be exported. Inside it two directories will be created: `playlists` where they will be exported in CSV files and `dumps` where they will be dumped into JSON files.
- `--clear` (_optional_): if "yes" clears output directory before exporting files.
- `--sep` (_optional_): separator in CSV files (by default is `^`).

## `get-playlists-stats.py`
This script gets various stats from playlist(s). Arguments:
- `--playlists` (_optional_): can be "all" to work on all playlists from given user or contain a list of playlists ids separated by comma. If omitted playlists are retrieved from `get-playlists-stats.txt`.
- `--maxstats` (_optional_): maximum number of items in each stat (by default is 10).

`--user` argument is only needed when using `--playlists all`.

## `list-playlists-artists.py`
This script lists all artists from given playlists, showing id and name of each one, sorted by name (can be useful for `merge-playlists.py`). Arguments:
- `--playlists` (_optional_): can be "all" to work on all playlists from given user or contain a list of playlists ids separated by comma. If omitted playlists are retrieved from `list-playlists-artists.txt`.
- `--listfile` (_optional_): path of text file where list should be written, if not provided list will only be printed to console.

## `list-user-playlists.py`
This script lists all playlists of given user, showing id and name of each one. Arguments:
- `--listfile` (_optional_): path of text file where list should be written, if not provided list will only be printed to console.

## `merge-playlists.py`
This script merges playlists. Input file is in JSON format instead of .txt to be more flexible, here is a quick explanation of fields:
- `source playlists ids`: ids of playlists that need to be merged, separated by space.
- `dest playlist id`: id of playlist containing all tracks from source playlists.
- `exclude artists ids` (_optional_): can be used to exclude artists from source playlists.
- `sorting` (_optional_): can be used to sort final playlist, accepted values are `title` and `artist`.
- `description`: this field is ignored by the script, can be used to write a description of each merge.

Arguments:
- `--file` (_optional_): can be used to specify an input file, if not provided the script uses `merge-playlists.json`.

`--user` argument is not needed by this script.

## `sort-playlists.py`
This script sorts tracks in given playlist(s). If a file named `sort-playlists-by-title.txt` exists playlists inside it are sorted by title; similarly if `sort-playlists-by-artist.txt` exists a sorting by artist is operated. `--user` argument is omitted to make the script work only on selected playlists and avoid modifications on all playlists by accident; to sort all playlists use `python list-user-playlists.py --listfile sort-playlists-by-title.txt` or `python list-user-playlists.py --listfile sort-playlists-by-artist.txt` before launching the script.
