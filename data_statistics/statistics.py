import argparse
import track_handler
import utils

parser = argparse.ArgumentParser(description='Read metadata, calculate statistics and display them')
parser.add_argument('--slakh-path', default='', help='path to slakh data source')
parser.add_argument('--medleydb-path', default='', help='path to medleydb data source')
parser.add_argument('--cambridge-path', default='', help='path to cambridge data source')
parser.add_argument('--rockband-path', default='', help='path to rockband data source')
parser.add_argument('--target-instruments', nargs='*', help='instrument to look for in cambridge and rockband data')
parser.add_argument('--save-frequency', type=int, default=10,
                    help='after how many tracks should info be written to file')
parser.add_argument('--tracks-filename', help='the name of the file to write data to')
args = parser.parse_args()

if args.target_instruments is not None:
    args.target_instruments.sort()

track_database = track_handler.get_tracks(args)

unique_instruments = []
tracks_with_piano = 0
tracks_with_guitar = 0
tracks_with_distorted_guitar = 0

for track in track_database.get_tracks():
    has_piano = False
    has_guitar = False
    has_distorted_guitar = False
    for instrument in track['instruments']:
        if type(instrument) == str:
            instrument = utils.normalize_instrument_name(instrument)
            if instrument == 'piano':
                has_piano = True
            if instrument == 'guitar':
                has_guitar = True
            if instrument == 'distorted_guitar':
                has_distorted_guitar = True

        if instrument not in unique_instruments:
            unique_instruments.append(instrument)

    if has_piano:
        tracks_with_piano += 1
    if has_guitar:
        tracks_with_guitar += 1
    if has_distorted_guitar:
        tracks_with_distorted_guitar += 1

print()
print('Tracks with piano: {0}'.format(str(tracks_with_piano)))
print('Tracks with guitar: {0}'.format(str(tracks_with_guitar)))
print('Tracks with distorted guitar: {0}'.format(str(tracks_with_distorted_guitar)))

print()
print('Updating instrument mapping for unknown instruments:')
instrument_mapping = track_database.get_instrument_mapping()
unknown_instruments_encountered = False
for instrument in unique_instruments:
    if instrument not in instrument_mapping:
        unknown_instruments_encountered = True
        print(instrument)
        group = input('Please tag this instrument with a fitting group: ')
        track_database.add_mapping(instrument, group)

print()
if unknown_instruments_encountered:
    track_database.save()
    print('Updated and saved instrument mappings to mapping.yaml')
else:
    print('All encountered instruments were already known')
