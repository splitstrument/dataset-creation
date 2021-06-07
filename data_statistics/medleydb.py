import utils
import os
import yaml


def parse_tracks(medleydb_path, track_database):
    track_counter = 0
    metadata_path = os.path.join(medleydb_path, 'metadata')
    for filename in os.listdir(metadata_path):
        track_folder_path = os.path.join(medleydb_path, filename.replace('_METADATA.yaml', ''))
        track_name = os.path.basename(track_folder_path)
        if not track_database.track_known(track_name) and os.path.isdir(track_folder_path):
            with open(os.path.join(metadata_path, filename)) as file:
                metadata = yaml.load(file, Loader=yaml.FullLoader)
                instruments = []
                stems = {}
                for key, stem in metadata['stems'].items():
                    instrument = stem['instrument']

                    # this does not seem to be the case in any actually files we process,
                    # but the metadata of MedleyDB contains some
                    if type(instrument) == list:
                        instrument = '|'.join(sorted(instrument))

                    instrument = utils.normalize_instrument_name(instrument)
                    if instrument in track_database.get_instrument_mapping():
                        instrument = track_database.get_instrument_mapping()[instrument]

                    instruments.append(instrument)
                    stems[key] = {
                        'instrument': instrument,
                        'path': os.path.join(
                            medleydb_path,
                            track_folder_path,
                            metadata['stem_dir'],
                            '{0}'.format(stem['filename'])
                        )
                    }
                stems['mix'] = {
                    'instrument': 'mix',
                    'path': os.path.join(medleydb_path, track_folder_path, '{0}'.format(metadata['mix_filename']))
                }
                track_database.save_track({
                    'instruments': instruments,
                    'stems': stems,
                    'name': track_name
                })
                track_counter += 1

    print('Parsed {0} MedleyDB tracks'.format(track_counter))
