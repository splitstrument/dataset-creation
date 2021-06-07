import os
import group_suggester


def parse_tracks(rockband_path, target_instruments, track_database):
    track_counter = 0
    for letter in os.listdir(rockband_path):
        letter_path = os.path.join(rockband_path, letter)
        for song in os.listdir(letter_path):
            if not track_database.track_known(song):
                song_folder = os.path.join(letter_path, song)

                available_instruments, stems = group_suggester.get_stems(target_instruments, track_database, song_folder)

                track_database.save_track({
                    'name': song,
                    'instruments': available_instruments,
                    'stems': stems
                })
                track_counter += 1

    print('Parsed {0} Rockband tracks'.format(track_counter))
