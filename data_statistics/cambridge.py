import os
import group_suggester


def parse_tracks(cambridge_path, target_instruments, track_database):
    track_counter = 0

    for track_name in os.listdir(cambridge_path):
        if not track_database.track_known(track_name):
            track_folder = os.path.join(cambridge_path, track_name)

            available_instruments, stems = group_suggester.get_stems(target_instruments, track_database, track_folder)

            track_database.save_track({
                'name': track_name,
                'instruments': available_instruments,
                'stems': stems
            })
            track_counter += 1

    print('Parsed {0} Cambridge tracks'.format(track_counter))
