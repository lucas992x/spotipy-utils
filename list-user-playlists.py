import argparse
from tools import spotipy_auth, get_user_playlists

def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', default = 'luca.s992')
    parser.add_argument('--auth', default = 'auto')
    parser.add_argument('--listfile', default = '')
    args = parser.parse_args()
    # authenticate
    sp = spotipy_auth(manual = (args.auth.lower() == 'manual'), modify = False)
    # get user playlists
    user_playlists = get_user_playlists(sp, args.user)
    lst = ''
    for playlist in user_playlists:
        lst += f'{playlist["id"]} {playlist["name"]}\n'
    if args.listfile:
        with open(args.listfile, 'w') as file:
            file.write(lst)
    else:
        print(f'Playlists of user {args.user} are:\n{lst}')

if __name__ == '__main__':
    main()
