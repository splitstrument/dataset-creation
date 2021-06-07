import argparse
import os
import sys
import yaml
import shutil
from helperutils.boolean_argparse import str2bool

parser = argparse.ArgumentParser(description='Move data sources to a uniform folder structure')
parser.add_argument('--tracks', default='tracks.yaml',
                    help='path to yaml file that contains information about tracks, generated from data_statistics')
parser.add_argument('--destination', required=True, help='path to root folder of new folder structure')
parser.add_argument('--copy-limit', type=int, help='how many tracks to copy at most')
parser.add_argument('--destructive-move', type=str2bool, default=False,
                    help='moves tracks instead of copying them, changing the original dataset')
parser.add_argument('--required-instruments', nargs='*',
                    help='only move tracks that have at least one stem of all given instruments')
args = parser.parse_args()

if not os.path.isfile(args.tracks):
    sys.exit('Provided path to tracks file is not a file')

if not os.path.isdir(args.destination):
    sys.exit('Provided path to destination is not a folder')

with open(args.tracks) as file:
    tracks = yaml.load(file, Loader=yaml.FullLoader)

index = 0
required_instruments = args.required_instruments
if required_instruments is None:
    required_instruments = []
for track in tracks:
    if not all([i in track['instruments'] for i in required_instruments]):
        continue
    name = track['name']
    track_folder = os.path.join(args.destination, name)
    if not os.path.isdir(track_folder):
        os.mkdir(track_folder)

    for key, stem in track['stems'].items():
        stem_folder = os.path.join(track_folder, stem['instrument'])
        if not os.path.isdir(stem_folder):
            os.mkdir(stem_folder)

        new_stem_path = os.path.join(stem_folder, os.path.basename(stem['path']))
        if os.path.isfile(stem['path']) and not os.path.isfile(new_stem_path):
            if args.destructive_move:
                shutil.move(stem['path'], stem_folder)
            else:
                shutil.copy(stem['path'], stem_folder)

    print('Organized track {0}'.format(name))
    index += 1
    if args.copy_limit is not None and index >= args.copy_limit:
        break
