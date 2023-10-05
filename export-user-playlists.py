import argparse, os.path, os, shutil, json
from tools import fix_file_name, spotipy_auth, get_user_playlists, get_playlist_tracks

# name is self-explanatory
def convert_ms_to_interval(ms, hours = True):
    ms = int(ms)
    seconds = int((ms / 1000) % 60)
    minutes = int((ms / (1000 * 60)) % 60)
    if hours:
        hours = int(ms / (1000 * 60 * 60))
        output = f'{str(hours)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}'
    else:
        output = f'{str(minutes).zfill(2)}:{str(seconds).zfill(2)}'
    return output

def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', default = 'luca.s992')
    parser.add_argument('--auth', default = 'auto')
    parser.add_argument('--dir', default = '')
    parser.add_argument('--clear', default = 'no')
    parser.add_argument('--sep', default = '^')
    args = parser.parse_args()
    # authenticate
    sp = spotipy_auth(manual = (args.auth.lower() == 'manual'), modify = False)
    user_playlists = get_user_playlists(sp, args.user)
    # setup
    if not os.path.isdir(args.dir):
        os.mkdir(args.dir)
    elif args.clear.lower() == 'yes':
        for item in os.listdir(args.dir):
            item_path = os.path.join(args.dir, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir:
                shutil.rmtree(item_path)
    exported_playlists_dir = os.path.join(args.dir, "playlists")
    if not os.path.isdir(exported_playlists_dir):
        os.mkdir(exported_playlists_dir)
    dumped_playlists_dir = os.path.join(args.dir, "dumps")
    if not os.path.isdir(dumped_playlists_dir):
        os.mkdir(dumped_playlists_dir)
    csv_fields = ['Title', 'Artist', 'Album', 'Duration', 'Id']
    for playlist in user_playlists:
        # set file paths
        file_name = fix_file_name(playlist["name"])
        export_file = f'{os.path.join(exported_playlists_dir, file_name)}.csv'
        dump_file = f'{os.path.join(dumped_playlists_dir, file_name)}.json'
        # retrieve songs
        items = get_playlist_tracks(sp, playlist['uri'])
        export_text = args.sep.join(csv_fields) + '\n'
        dump = []
        for item in items:
            dump.append(item)
            track = item['track']
            song_fields = [track['name']]
            # these checks are needed because podcasts don't have all fields
            if track.get('artists', None):
                song_fields.append(', '.join([artist['name'] for artist in track['artists']]))
            else:
                song_fields.append('')
            if track.get('album', None):
                song_fields.append(track['album']['name'])
            else:
                song_fields.append('')
            song_fields.append(convert_ms_to_interval(track['duration_ms']))
            song_fields.append(track['id'])
            export_text += args.sep.join(song_fields) + '\n'
        # write to text file(s)
        open(export_file, 'w').close()
        with open(export_file, 'w') as file:
            file.write(export_text)
        print(f'Playlist "{playlist["name"]}" exported to {export_file}')
        open(dump_file, 'w').close()
        with open(dump_file, 'w') as file:
            json.dump(dump, file, indent = 4)
        print(f'Playlist "{playlist["name"]}" dumped to {dump_file}')

if __name__ == '__main__':
    main()
