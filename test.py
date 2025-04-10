import json
from tools import spotipy_auth

sp = spotipy_auth(manual=True, modify=False)
playlist = sp.playlist("0Bj0DlaClFtpNSn48wgoMh")
# print(playlist)
# playlist.pop("tracks")
playlist["tracks"].pop("items")
with open("test.json", "w") as file:
    json.dump(playlist, file, indent=4)
