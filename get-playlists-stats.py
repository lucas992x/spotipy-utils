import argparse, sys, os.path, json
import pandas as pd
from tools import (
    spotipy_auth,
    read_ids_from_file,
    get_user_playlists,
    get_playlist_tracks,
    convert_ms_to_interval,
)


# function that updates playlists data with data from a specific playlist
def get_playlist_stats(playlist_tracks, tracks_data, single_artists, artists_durations, tracks_counter):  # fmt: skip
    for item in playlist_tracks:
        track = item["track"]
        if not track["episode"]:
            duration_ms = int(track["duration_ms"])
            datarow = {
                "Title": track["name"],
                "Duration-ms": duration_ms,
                "Duration": convert_ms_to_interval(duration_ms),
                "Id": track["id"],
            }
            if track.get("artists", None) is not None:
                splittedartists = [artist["name"] for artist in track["artists"]]
                single_artists += splittedartists
                datarow.update({"Artist": ", ".join(splittedartists)})
                for artist in splittedartists:
                    artist_duration = artists_durations.get(artist, 0) + duration_ms
                    artists_durations.update({artist: artist_duration})
            if track.get("album", None) is not None:
                datarow.update({"Album": track["album"]["name"]})
            tracks_data.loc[tracks_counter] = datarow
            tracks_counter += 1
    tracks_data = tracks_data.drop_duplicates()
    return tracks_data, single_artists, artists_durations, tracks_counter


# main function
def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="luca.s992")
    parser.add_argument("--auth", default="auto")
    parser.add_argument("--playlists", default="")
    parser.add_argument("--file", default="")
    parser.add_argument("--maxstats", default="10")
    args = parser.parse_args()
    # initialize playlist(s) data
    table_fields = ["Title", "Artist", "Album", "Duration", "Id", "Duration-ms"]
    tracks_data = pd.DataFrame(columns=table_fields)
    single_artists = []
    artists_durations = {}
    tracks_counter = 0
    # read data from playlist(s)
    if args.file:
        # try to read playlist items from file
        if not os.path.isfile(args.file):
            sys.exit(f"Cannot find playlist file {args.file}")
        with open(args.file, "r") as file:
            playlist_tracks = json.load(file)
        stats_playlists_names = f"'{os.path.splitext(os.path.basename(args.file))[0]}'"
        tracks_data, single_artists, artists_durations, tracks_counter = (
            get_playlist_stats(
                playlist_tracks,
                tracks_data,
                single_artists,
                artists_durations,
                tracks_counter,
            )
        )
    else:
        # authenticate
        sp = spotipy_auth(manual=(args.auth.lower() == "manual"), modify=False)
        # retrieve data from specified playlist(s)
        if args.playlists:
            if args.playlists.lower() == "all":
                stats_playlists = get_user_playlists(sp, args.user)
            else:
                stats_playlists = [sp.playlist(id) for id in args.playlists.split(",")]
        else:
            script_dir = os.path.dirname(__file__)
            stats_file = os.path.join(script_dir, "get-playlists-stats.txt")
            if not os.path.isfile(stats_file):
                sys.exit(f"Cannot find stats file {stats_file}")
            ids = read_ids_from_file(stats_file)
            stats_playlists = []
            for id in ids:
                stats_playlists.append(sp.playlist(id))
        stats_playlists_names = ", ".join([f'"{playlist["name"]}"' for playlist in stats_playlists])  # fmt: skip
        for playlist in stats_playlists:
            playlist_tracks = get_playlist_tracks(sp, playlist["uri"])
            tracks_data, single_artists, artists_durations, tracks_counter = (
                get_playlist_stats(
                    playlist_tracks,
                    tracks_data,
                    single_artists,
                    artists_durations,
                    tracks_counter,
                )
            )
    # count unique artists
    artists_counter = pd.DataFrame({"Artist": single_artists})
    # print stuff
    print(f"Stats for playlists {stats_playlists_names}\n")
    print(f'Total songs: {tracks_data["Id"].nunique()}')
    print(f"Total artists: {len(list(set(single_artists)))}")
    print(f'Total albums: {tracks_data["Album"].nunique()}')
    print(f'Total duration: {convert_ms_to_interval(tracks_data["Duration-ms"].sum())}')
    print(f'Average duration: {convert_ms_to_interval(tracks_data["Duration-ms"].mean())}\n')  # fmt: skip
    print(f"Most frequent artists:\n")
    tracks_data = tracks_data.drop("Id", axis=1)
    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        # print most frequent artists
        max_stats = min(int(args.maxstats), len(artists_counter.index))
        print(artists_counter["Artist"].value_counts()[:max_stats].to_string())
        # print artists with most and least cumulative duration
        cumulative_durations = {
            artist: [
                artists_durations[artist],
                convert_ms_to_interval(artists_durations[artist]),
            ]
            for artist in artists_durations
        }
        cumulative_durations = pd.DataFrame.from_dict(cumulative_durations, orient="index")  # fmt: skip
        if int(args.maxstats) >= len(cumulative_durations.index) / 2:
            cumulative_durations = cumulative_durations.sort_values(0, axis=0, ascending=False).drop(0, axis=1)  # fmt: skip
            print(f"\nCumulative durations:")
            print(cumulative_durations.to_string())
        else:
            max_stats = min(int(args.maxstats), len(cumulative_durations.index))
            longest = cumulative_durations.sort_values(0, axis=0, ascending=False).drop(0, axis=1)[:max_stats]  # fmt: skip
            shortest = cumulative_durations.sort_values(0, axis=0, ascending=True).drop(0, axis=1)[:max_stats]  # fmt: skip
            print("\nMaximum cumulative durations:")
            print(longest.to_string())
            print("\nMinimum cumulative durations:")
            print(shortest.to_string())
        # print longest and shortest songs
        if int(args.maxstats) >= len(tracks_data.index) / 2:
            durations = (
                tracks_data.sort_values("Duration-ms", axis=0, ascending=False)
                .drop("Duration-ms", axis=1)
                .drop("Album", axis=1)
            )
            print(f"\nSongs sorted by duration:\n{durations.to_string(index = False)}")
        else:
            max_stats = min(int(args.maxstats), len(tracks_data.index))
            longest = (
                tracks_data.sort_values("Duration-ms", axis=0, ascending=False)
                .drop("Duration-ms", axis=1)
                .drop("Album", axis=1)[:max_stats]
            )
            shortest = (
                tracks_data.sort_values("Duration-ms", axis=0, ascending=True)
                .drop("Duration-ms", axis=1)
                .drop("Album", axis=1)[:max_stats]
            )
            print("\nLongest songs:")
            print(longest.to_string(index=False))
            print("\nShortest songs:")
            print(shortest.to_string(index=False))


# invoke main function
if __name__ == "__main__":
    main()
