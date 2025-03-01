import argparse
from tools import spotipy_auth, sort_playlist_tracks


# main function
def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth", default="auto")
    parser.add_argument("--playlists", default="")
    args = parser.parse_args()
    # authenticate
    sp = spotipy_auth(manual=(args.auth.lower() == "manual"), modify=True)
    # shuffle playlist(s) randomly
    shuffle_playlists_ids = args.playlists.split(",")
    for id in shuffle_playlists_ids:
        print(f'Sorting tracks in "{sp.playlist(id)["name"]}" randomly')
        sort_playlist_tracks(sp, id, "random")
        # print(f'Sorted tracks in "{sp.playlist(id)["name"]}" randomly')


# invoke main function
if __name__ == "__main__":
    main()
