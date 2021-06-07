import os
import argparse
from helperutils.stemloader import StemLoader

stem_loader = StemLoader()

parser = argparse.ArgumentParser(description='Check amount of silence and ratio to audible data in tracks')
parser.add_argument('--source-folder', required=True, help='path to folder containing training data')
parser.add_argument('--save-to-folder', required=True, help='path to folder to save cut songs')
parser.add_argument('--length', required=True, help='desired song length in s')
args = parser.parse_args()


def cut_song_slices(sound_length, desired_length, song, track):
    desired_length_ms = int(desired_length) * 1000
    current_song_length = desired_length_ms
    cuts = []
    print(current_song_length)
    print(sound_length)
    first_cut = song[:current_song_length]
    cuts.append(first_cut)
    while current_song_length < int(sound_length):
        cut = song[current_song_length:current_song_length + desired_length_ms]
        cuts.append(cut)
        current_song_length += desired_length_ms
        print(current_song_length)

    index = 0
    for cut_song in cuts:
        print("EXPORTING")
        cut_track_path = os.path.join(args.save_to_folder, '%s_%s.wav' % (track, str(index)))
        cut_song.export(cut_track_path, format='wav')
        index = index + 1


source_folder = args.source_folder
for track in os.listdir(source_folder):
    track_path = os.path.join(source_folder, track)
    sound = stem_loader.get_stem(track_path)
    cut_song_slices(len(sound), args.length, sound, track)
