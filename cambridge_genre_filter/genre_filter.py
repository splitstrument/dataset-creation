import os
import argparse
from html_table_parser import HTMLTableParser
from collections import defaultdict

parser = argparse.ArgumentParser(description='Find genres of a folder of cambridge songs')
parser.add_argument('--cambridge-folder', required=True, help='path to cambridge songs')
args = parser.parse_args()

genre_songs = {}
tables_folder = os.path.join(os.path.dirname(__file__), 'genre_tables')
for table_name in os.listdir(tables_folder):
    table_path = os.path.join(tables_folder, table_name)
    with open(table_path, 'r') as table_file:
        reader = HTMLTableParser()
        reader.feed(table_file.read())
        song_table = reader.tables[0][1:]
        songs = []
        for song in song_table:
            song_name = '%s_%s' % (song[0], song[1])
            song_name = song_name.replace('\'', '')
            song_name = song_name.replace(' ', '')
            song_name = song_name.replace('%', 'And')
            song_name = song_name.lower()
            songs.append(song_name)

        genre_songs[table_name.replace('.html', '')] = songs

genre_counts = defaultdict(int)
for track in os.listdir(args.cambridge_folder):
    track = track.lower()
    for genre, songs in genre_songs.items():
        for song in songs:
            if song in track:
                genre_counts[genre] += 1

total_count = 0
for genre, count in genre_counts.items():
    print('%s: %i' % (genre, count))
    total_count += count
print('Total songs from Cambridge set: %i' % total_count)
