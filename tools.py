import spotipy, random, string
from spotipy.oauth2 import SpotifyOAuth


# fix file name by trimming it and replacing characters that cannot be used
def fix_file_name(name):
    name = name.strip()
    chars = r'\/:*?"<>|'
    for char in chars:
        name = name.replace(char, "_")
    return name


# Authentication; 'manual' can be used when opening browser has issues or is not
# possible at all (e.g. CLI-only environments), 'modify' should be set to True if
# playlists need to be modified instead of just read.
def spotipy_auth(manual=False, modify=False):
    scope = "playlist-read-private playlist-read-collaborative"
    if modify:
        scope += " playlist-modify-private playlist-modify-public"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, open_browser=(not manual)))  # fmt: skip
    return sp


# retrieve all playlists from given user
def get_user_playlists(sp, username):
    playlists = sp.user_playlists(username)
    return playlists["items"]


# read ids of playlists from text file where each row contains playlist id and,
# optionally, additional text (e.g. playlist name) separated by space; examples
# are included in this repository
def read_ids_from_file(filepath):
    ids = []
    with open(filepath, "r") as file:
        for line in file:
            if " " in line:
                id = line.strip().split(" ")[0]
            else:
                id = line.strip()
            ids.append(id)
    return ids


# retrieve songs from a playlist given its id
def get_playlist_tracks(sp, playlist_id):
    results = sp.playlist_items(playlist_id)
    tracks = results["items"]
    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])
    return tracks


# convert an amount of time in milliseconds to a string in format 'hh:mm:ss' or 'mm:ss'
def convert_ms_to_interval(ms, hours=True):
    ms = int(ms)
    seconds = int((ms / 1000) % 60)
    minutes = int((ms / (1000 * 60)) % 60)
    output = f"{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"
    if hours:
        hours = int(ms / (1000 * 60 * 60))
        output = f"{str(hours)}:{output}"
    return output


# sort tracks in playlist
def sort_playlist_tracks(sp, playlist_id, by):
    items = get_playlist_tracks(sp, playlist_id)
    tracks = []
    for item in items:
        track = item["track"]
        # to improve sorting everything is lowercased, spaces are removed, exclamation
        # mark is used as separator to correctly sort tracks with same or similar fields
        title = track["name"]
        artists = ", ".join([a["name"] for a in track["artists"]])
        album = track["album"]["name"]
        if by == "title":
            fields = [title, artists, album]
        elif by == "artist":
            fields = [artists, album, title]
        elif by == "random":
            fields = [
                "".join(
                    random.choices(
                        string.ascii_uppercase + string.ascii_lowercase + string.digits,
                        k=100,
                    )
                )
            ]
        tracks.append("!".join(fields).lower().replace(" ", ""))
    # create a copy of tracks list, sort it and compare the two lists: if they
    # are different move each track in playlist to its new index
    sorted_tracks = tracks[:]
    sorted_tracks.sort()
    if tracks != sorted_tracks:
        for track in sorted_tracks:
            old_index = tracks.index(track)
            new_index = sorted_tracks.index(track)
            if new_index != old_index:
                sp.playlist_reorder_items(playlist_id, old_index, new_index)
                tracks.insert(new_index, tracks.pop(old_index))
