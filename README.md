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
- `--user`: Spotify username (explained above), only needed in scripts that don't perform modify operations on playlists (unless otherwise specified).
- `--auth`: authentication mode, by default is `auto` but can be set to `manual` when opening browser has issues or is not possible at all (e.g. in CLI-only environments).

Here are other common usages:
- All `.txt` files used as input by scripts should be placed in script's directory and contain in each row a playlist id and, optionally, additional text (e.g. playlist name) separated by space; the same format is used by `list-user-playlists.py`'s output, so it's easier to run it and pick needed playlists rather than getting ids one by one from Spotify. Examples are included in this repository.
- All arguments that contain playlists ids should have them separated by comma. In some cases this argument can be `all` to work automatically on all user's playlists; some scripts don't allow this to prevent modifications on all playlists made by accident, but it's possible to automatically generate a file with all playlists by using `python list-user-playlists.py --listfile <file-name>.txt`.

## `export-playlists.py`
This script exports all playlists of given user. Arguments:
- `--dir` (_optional_): path of directory where files will be exported. Inside it two directories will be created: `playlists` where they will be exported in CSV files and `dumps` where they will be dumped into JSON files.
- `--clear` (_optional_): if `yes` clears output directory before exporting files.
- `--sep` (_optional_): separator in CSV files (by default is `^`).

## `get-playlists-stats.py`
This script gets various stats from playlist(s). Arguments:
- `--playlists` (_optional_): ids of playlists (can be `all`), if omitted playlists are retrieved from `get-playlists-stats.txt`.
- `--file` (_optional_): can be used to specify path of a JSON file where a playlist was dumped, so that playlist data is retrieved from it without having to retrieve playlist again from Spotify.
- `--maxstats` (_optional_): maximum number of items in each stat (by default is 10).

`--user` argument is only needed when using `--playlists all`.

## `list-playlists-artists.py`
This script lists all artists from given playlists, showing id and name of each one, sorted by name (can be useful for `merge-playlists.py`). Arguments:
- `--playlists` (_optional_): ids of playlists to work on (can be `all`), if omitted playlists are retrieved from `list-playlists-artists.txt` if exists.
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

## `shuffle-playlists.py`
This script sorts playlist(s) randomly. Arguments:
- `--playlists`: ids of playlists to sorted randomly (cannot be `all`), if omitted playlists are retrieved from `shuffle-playlists.txt` if exists.
- `--portion` (_optional_): can be used to move only last tracks to random positions, may be a number or a percentage (e.g. `10%`).

## `sort-playlists.py`
This script sorts tracks in given playlist(s). Arguments:
- `--bytitle` (_optional_): ids of playlists to sort by title (cannot be `all`), if omitted playlists are retrieved from `sort-playlists-by-title.txt` if exists.
- `--byartist` (_optional_): ids of playlists to sort by artist (cannot be `all`), if omitted playlists are retrieved from `sort-playlists-by-artist.txt` if exists.
