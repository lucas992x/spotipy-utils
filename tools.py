import spotipy, random, string
from spotipy.oauth2 import SpotifyOAuth
from time import sleep


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


# move track in specified position of given playlist
def move_track_in_playlist(sp, playlist_id, old_index, new_index):
    # try multiple times because for big playlists may exceed time out; if an error
    # occurs wait some time before retrying and increase wait time for next error
    retry_counter = 0
    max_retries = 5
    wait_time = 5
    done = False
    while not done:
        # try to put current track in desired position
        try:
            sp.playlist_reorder_items(playlist_id, old_index, new_index)
            done = True
        # check if max retries were reached
        except Exception as e:
            if retry_counter == max_retries - 1:
                raise
            else:
                retry_counter += 1
                print(
                    "Error while moving track from index {} to {}, retry {} of {}; waiting {} before retrying".format(
                        old_index, new_index, retry_counter, max_retries, wait_time
                    )
                )
                print(e)
                sleep(wait_time)
                wait_time *= 2


# sort tracks in playlist
def sort_playlist_tracks(sp, playlist_id, by, portion=None):
    # retrieve all playlist tracks
    items = get_playlist_tracks(sp, playlist_id)
    # check if only last portion of playlist should be sorted, in that case all
    # tracks from starting index will be moved in a random position before it (only
    # used with random sorting)
    if portion:
        if portion.endswith("%"):
            num_perc = float(portion.replace("%", "")) / 100
            start_index = round(len(items) * (1 - num_perc))
        else:
            start_index = len(items) - int(portion)
        for old_index in range(start_index, len(items)):
            new_index = random.randint(0, start_index - 1)
            move_track_in_playlist(sp, playlist_id, old_index, new_index)
    else:
        # initialize list of tracks as strings
        tracks = []
        for j in range(len(items)):
            if by == "random":
                # generate random alphanumeric string to sort tracks randomly
                choices = (string.ascii_uppercase + string.ascii_lowercase + string.digits)  # fmt: skip
                fields = ["".join(random.choices(choices, k=100))]
            else:
                # retrieve playlist data to sort it
                item = items[j]
                track = item["track"]
                # to improve sorting everything is lowercased, spaces are
                # removed, exclamation mark is used as separator to correctly
                # sort tracks with same or similar fields
                title = track["name"]
                artists = ", ".join([a["name"] for a in track["artists"]])
                album = track["album"]["name"]
                if by == "title":
                    fields = [title, artists, album]
                elif by == "artist":
                    fields = [artists, album, title]
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
                    move_track_in_playlist(sp, playlist_id, old_index, new_index)
                    tracks.insert(new_index, tracks.pop(old_index))
