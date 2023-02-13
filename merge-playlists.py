import argparse, os, os.path, json
from tools import spotipy_auth, get_user_playlists, get_playlist_tracks, sort_playlist_tracks

def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--auth', default = 'auto')
    parser.add_argument('--file', default = '')
    args = parser.parse_args()
    # read input file
    if args.file:
        input_file = args.file
    else:
        script_dir = os.path.dirname(__file__)
        input_file = os.path.join(script_dir, 'merge-playlists.json')
    with open(input_file, 'r') as json_file:
        merge_tasks = json.load(json_file)
    # authenticate
    sp = spotipy_auth(manual = (args.auth.lower() == 'manual'), modify = True)
    # perform merge tasks
    for task in merge_tasks:
        # read input
        excluded_artists_ids = task.get('exclude artists ids', '').split(' ')
        source_playlists_ids = task['source playlists ids'].split(' ')
        dest_playlist_id = task['dest playlist id']
        dest_playlist_name = sp.playlist(dest_playlist_id)['name']
        source_items = []
        for playlist_id in source_playlists_ids:
            source_items += get_playlist_tracks(sp, playlist_id)
        source_tracks_uris = [item['track']['uri'] for item in source_items]
        source_tracks_ids = [item['track']['id'] for item in source_items]
        dest_items = get_playlist_tracks(sp, dest_playlist_id)
        # remove tracks that are not in source playlists
        dest_tracks_ids_remove = [item['track']['id'] for item in dest_items if item['track']['id'] not in source_tracks_ids]
        if len(dest_tracks_ids_remove) > 0:
            print(f'Removing {len(dest_tracks_ids_remove)} exceeding track(s) from "{dest_playlist_name}"')
            sp.playlist_remove_all_occurrences_of_items(dest_playlist_id, dest_tracks_ids_remove)
        else:
            print(f'Nothing to remove from "{dest_playlist_name}"')
        # add missing tracks from source playlists
        dest_tracks_ids = [item['track']['id'] for item in dest_items]
        source_tracks_uris_add = list(set([item['track']['uri'] for item in source_items if item['track']['id'] not in dest_tracks_ids and not (set([artist['id'] for artist in item['track']['artists']]) & set(excluded_artists_ids))]))
        if len(source_tracks_uris_add) > 0:
            print(f'Adding {len(source_tracks_uris_add)} missing track(s) to "{dest_playlist_name}"')
            sp.playlist_add_items(dest_playlist_id, source_tracks_uris_add)
        else:
            print(f'No tracks to add to "{dest_playlist_name}"')
        # sort dest playlist if requested
        sorting = task.get('sorting', None)
        if sorting:
            sort_playlist_tracks(sp, dest_playlist_id, sorting)

if __name__ == '__main__':
    main()
