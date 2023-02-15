import argparse, os.path, re
from tools import spotipy_auth, read_ids_from_file, get_user_playlists, get_playlist_tracks

def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', default = 'luca.s992')
    parser.add_argument('--auth', default = 'auto')
    parser.add_argument('--playlists', default = '')
    parser.add_argument('--listfile', default = '')
    args = parser.parse_args()
    # authenticate
    sp = spotipy_auth(manual = (args.auth.lower() == 'manual'), modify = False)
    # get list of playlists
    if args.playlists:
        if args.playlists.lower() == 'all':
            playlists = get_user_playlists(sp, args.user)
        else:
            playlists = [sp.playlist(id) for id in args.playlists.split(',')]
    else:
        script_dir = os.path.dirname(__file__)
        artists_file = os.path.join(script_dir, 'list-playlists-artists.txt')
        ids = read_ids_from_file(artists_file)
        playlists = []
        for id in ids:
            playlists.append(sp.playlist(id))
    # read data from playlist(s)
    artists = []
    for playlist in playlists:
        items = get_playlist_tracks(sp, playlist['uri'])
        for item in items:
            track = item['track']
            playlist_artists = track.get('artists', None)
            if playlist_artists is not None:
                new_artists = [f'{artist["name"]} {artist["id"]}' for artist in playlist_artists]
                artists = list(set(artists + new_artists))
    # sort artists by name ignoring case
    artists = sorted(artists, key = str.casefold)
    # move artists ids at beginning of each line and convert to string
    artists = '\n'.join([re.sub(r'^(.+) (\S+)$', r'\2 \1', line) for line in artists])
    if args.listfile:
        with open(args.listfile, 'w') as file:
            file.write(artists + '\n')
    else:
        print(artists)

if __name__ == '__main__':
    main()
