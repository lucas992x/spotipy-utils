import argparse, os.path, os, shutil, json
from tools import fix_file_name, spotipy_auth, get_user_playlists, get_playlist_tracks


# delete content of given directory without deleting directory itself
def clear_dir(dir_path):
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            os.unlink(item_path)
        elif os.path.isdir:
            shutil.rmtree(item_path)


# name is self-explanatory
def convert_ms_to_interval(ms, hours=True):
    ms = int(ms)
    seconds = int((ms / 1000) % 60)
    minutes = int((ms / (1000 * 60)) % 60)
    if hours:
        hours = int(ms / (1000 * 60 * 60))
        output = f"{str(hours)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"
    else:
        output = f"{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"
    return output


def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="luca.s992")
    parser.add_argument("--auth", default="auto")
    parser.add_argument("--dir", default="")
    parser.add_argument("--clear", default="no")
    parser.add_argument("--sep", default="^")
    args = parser.parse_args()
    # authenticate
    sp = spotipy_auth(manual=(args.auth.lower() == "manual"), modify=False)
    user_playlists = get_user_playlists(sp, args.user)
    # set variables
    dumped_playlists_dir = os.path.join(args.dir, "dumps")
    exported_playlists_dir = os.path.join(args.dir, "playlists")
    csv_fields = ["Title", "Artist", "Album", "Duration", "Id"]
    # create/delete directories if needed
    if not os.path.isdir(args.dir):
        os.mkdir(args.dir)
        os.mkdir(dumped_playlists_dir)
        os.mkdir(exported_playlists_dir)
    else:
        if not os.path.isdir(dumped_playlists_dir):
            os.mkdir(dumped_playlists_dir)
        elif args.clear.lower() == "yes":
            clear_dir(dumped_playlists_dir)
        if not os.path.isdir(dumped_playlists_dir):
            os.mkdir(exported_playlists_dir)
        elif args.clear.lower() == "yes":
            clear_dir(exported_playlists_dir)
    # export playlists
    for playlist in user_playlists:
        try:
            # print playlist name
            playlist_name = playlist["name"]
            print(f'Exporting playlist "{playlist_name}"')
            # set file paths
            file_name = fix_file_name(playlist_name)
            dump_file = f"{os.path.join(dumped_playlists_dir, file_name)}.json"
            export_file = f"{os.path.join(exported_playlists_dir, file_name)}.csv"
            # retrieve songs
            items = get_playlist_tracks(sp, playlist["uri"])
            # write dump to JSON file
            open(dump_file, "w").close()
            with open(dump_file, "w") as file:
                json.dump(items, file, indent=4)
            print(f'Playlist "{playlist["name"]}" dumped to {dump_file}')
            # create CSV with tracks
            export_text = args.sep.join(csv_fields) + "\n"
            for item in items:
                track = item["track"]
                # for unknown reason I found a non-track item in a dump, this check avoids issues
                if track is None:
                    print("Found non-track item")
                else:
                    song_fields = []
                    # these checks are performed because podcasts don't have all fields
                    if track.get("name", None):
                        song_fields.append(track["name"])
                    else:
                        song_fields.append("")
                    if track.get("artists", None):
                        song_fields.append(", ".join([artist["name"] for artist in track["artists"]]))  # fmt: skip
                    else:
                        song_fields.append("")
                    if track.get("album", None):
                        song_fields.append(track["album"]["name"])
                    else:
                        song_fields.append("")
                    song_fields.append(convert_ms_to_interval(track["duration_ms"]))
                    song_fields.append(track["id"])
                    export_text += args.sep.join(song_fields) + "\n"
            # write playlist to CSV file
            open(export_file, "w").close()
            with open(export_file, "w") as file:
                file.write(export_text)
            print(f'Playlist "{playlist["name"]}" exported to {export_file}')
        except Exception as e:
            print(f"Error occurred with playlist: {e}")


if __name__ == "__main__":
    main()
