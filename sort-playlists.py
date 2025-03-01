import argparse, os.path
from tools import spotipy_auth, read_ids_from_file, sort_playlist_tracks


# main function
def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth", default="auto")
    args = parser.parse_args()
    # authenticate
    sp = spotipy_auth(manual=(args.auth.lower() == "manual"), modify=True)
    # sort playlist(s)
    script_dir = os.path.dirname(__file__)
    sort_title_file = os.path.join(script_dir, "sort-playlists-by-title.txt")
    sort_artist_file = os.path.join(script_dir, "sort-playlists-by-artist.txt")
    sort_playlists = [[sort_title_file, "title"], [sort_artist_file, "artist"]]
    for item in sort_playlists:
        sort_file, by = item
        if os.path.isfile(sort_file):
            sort_playlists_ids = read_ids_from_file(sort_file)
            for id in sort_playlists_ids:
                print(f'Sorting tracks in "{sp.playlist(id)["name"]}" by {by}')
                sort_playlist_tracks(sp, id, by)
                # print(f'Sorted tracks in "{sp.playlist(id)["name"]}" by {by}')


# invoke main function
if __name__ == "__main__":
    main()
