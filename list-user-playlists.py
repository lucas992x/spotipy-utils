import argparse
from tools import spotipy_auth, get_user_playlists


# main function
def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="luca.s992")
    parser.add_argument("--auth", default="auto")
    parser.add_argument("--listfile", default="")
    args = parser.parse_args()
    # authenticate
    sp = spotipy_auth(manual=(args.auth.lower() == "manual"), modify=False)
    # get user playlists
    user_playlists = get_user_playlists(sp, args.user)
    lst = ""
    for playlist in user_playlists:
        # try to append playlist ID and name
        try:
            lst += f'{playlist["id"]} {playlist["name"]}\n'
        # print error details
        except Exception as e:
            print(f"Error occurred with playlist: {e}")
    # check if output list should be printed to console or written to file
    if args.listfile:
        with open(args.listfile, "w") as file:
            file.write(lst)
    else:
        print(f"Playlists of user {args.user} are:\n{lst}")


# invoke main function
if __name__ == "__main__":
    main()
