import utils
import os
import yaml


def parse_tracks(slakh_path, track_database):
    track_counter = 0
    for root, dirs, files in os.walk(slakh_path):
        dirs[:] = [d for d in dirs if not (d.endswith('omitted') or d.endswith('MIDI') or d.endswith('stems'))]
        if 'metadata.yaml' in files:
            with open(os.path.join(root, 'metadata.yaml')) as file:
                metadata = yaml.load(file, Loader=yaml.FullLoader)
                song_uuid = metadata['UUID']
                if not track_database.track_known(song_uuid):
                    instruments = []
                    stems = {}
                    for key, stem in metadata['stems'].items():
                        if stem['audio_rendered']:
                            instrument = utils.normalize_instrument_name(stem['midi_program_name'])
                            if instrument in track_database.get_instrument_mapping():
                                instrument = track_database.get_instrument_mapping()[instrument]

                            instruments.append(instrument)
                            stems[key] = {
                                'instrument': instrument,
                                'path': os.path.join(root, 'stems', '{0}.flac'.format(key))
                            }
                    stems['mix'] = {
                        'instrument': 'mix',
                        'path': os.path.join(root, 'mix.flac')
                    }
                    track_database.save_track({'instruments': instruments, 'stems': stems, 'name': song_uuid})
                    track_counter += 1

    print('Parsed {0} Slakh tracks'.format(track_counter))
