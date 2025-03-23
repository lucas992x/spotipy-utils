import argparse, os.path
from tools import spotipy_auth, read_ids_from_file, sort_playlist_tracks


# main function
def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth", default="auto")
    parser.add_argument("--playlists", default="")
    parser.add_argument("--portion", default="")
    args = parser.parse_args()
    # authenticate
    sp = spotipy_auth(manual=(args.auth.lower() == "manual"), modify=True)
    # get script directory
    script_dir = os.path.dirname(__file__)
    # check if an argument was passed to specify playlist(s) to be shuffled
    if args.playlists:
        playlists_ids = args.playlists.split(",")
    else:
        sort_playlists_file = os.path.join(script_dir, "shuffle-playlists.txt")
        if os.path.isfile(sort_playlists_file):
            playlists_ids = read_ids_from_file(sort_playlists_file)
    # sort playlist(s) randomly
    for id in playlists_ids:
        print_message = f'Sorting tracks in "{sp.playlist(id)["name"]}" randomly'
        if args.portion:
            print_message += f" (last {args.portion})"
        print(print_message)
        sort_playlist_tracks(sp, id, "random", args.portion)
        # print(f'Sorted tracks in "{sp.playlist(id)["name"]}" randomly')


# invoke main function
if __name__ == "__main__":
    main()
