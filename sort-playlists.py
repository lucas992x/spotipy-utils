import argparse, os.path
from tools import spotipy_auth, read_ids_from_file, sort_playlist_tracks


# main function
def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth", default="auto")
    parser.add_argument("--bytitle", default="")
    parser.add_argument("--byartist", default="")
    args = parser.parse_args()
    # authenticate
    sp = spotipy_auth(manual=(args.auth.lower() == "manual"), modify=True)
    # get script directory
    script_dir = os.path.dirname(__file__)
    # initialize list of playlists to sort, each item will contain id and sorting criteria
    sort_playlists = []
    # check if an argument was passed to specify playlist(s) to be sorted by title
    if args.bytitle:
        sort_playlists += [[id, "title"] for id in args.bytitle.split(",")]
    else:
        sort_bytitle_file = os.path.join(script_dir, "sort-playlists-by-title.txt")
        if os.path.isfile(sort_bytitle_file):
            sort_bytitle_playlists_ids = read_ids_from_file(sort_bytitle_file)
            sort_playlists += [[id, "title"] for id in sort_bytitle_playlists_ids]
    # check if an argument was passed to specify playlist(s) to be sorted by artist
    if args.byartist:
        sort_playlists += [[id, "artist"] for id in args.byartist.split(",")]
    else:
        sort_byartist_file = os.path.join(script_dir, "sort-playlists-by-artist.txt")
        if os.path.isfile(sort_byartist_file):
            sort_byartist_playlists_ids = read_ids_from_file(sort_byartist_file)
            sort_playlists += [[id, "artist"] for id in sort_byartist_playlists_ids]
    # sort playlist(s) by selected criteria
    for item in sort_playlists:
        id, by = item
        print(f'Sorting tracks in "{sp.playlist(id)["name"]}" by {by}')
        sort_playlist_tracks(sp, id, by)
        # print(f'Sorted tracks in "{sp.playlist(id)["name"]}" by {by}')


# invoke main function
if __name__ == "__main__":
    main()
