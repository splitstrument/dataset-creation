import os
import hashlib
import slakh
import medleydb
import cambridge
import rockband
from track_database import TrackDatabase


def get_tracks(args):
    if args.tracks_filename is None:
        args_hash = hashlib.md5(
            (
                    args.slakh_path
                    + args.medleydb_path
                    + args.cambridge_path
                    + ''.join(args.target_instruments)
                    + args.rockband_path
            ).encode()
        )
        tracks_filename = 'tracks_{0}.yaml'.format(args_hash.hexdigest())
    else:
        tracks_filename = args.tracks_filename
    tracks_filepath = os.path.join(os.path.abspath(os.getcwd()), tracks_filename)

    mapping_filepath = os.path.join(os.path.abspath(os.getcwd()), 'mapping.yaml')

    track_database = TrackDatabase(tracks_filepath, mapping_filepath, args.save_frequency)

    if args.slakh_path != '' and os.path.isdir(args.slakh_path):
        slakh.parse_tracks(args.slakh_path, track_database)
    if args.medleydb_path != '' and os.path.isdir(args.medleydb_path):
        medleydb.parse_tracks(args.medleydb_path, track_database)
    if args.cambridge_path != '' and args.target_instruments != '' and os.path.isdir(args.cambridge_path):
        cambridge.parse_tracks(
            args.cambridge_path,
            args.target_instruments,
            track_database
        )
    if args.rockband_path != '' and args.target_instruments != '' and os.path.isdir(args.rockband_path):
        rockband.parse_tracks(
            args.rockband_path,
            args.target_instruments,
            track_database
        )

    track_database.save()
    return track_database
