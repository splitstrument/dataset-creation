import os
import utils
from helperutils.audio_file_checker import is_accepted_audio_file


def invert_mapping(instrument_mapping):
    inverted_mapping = dict()
    for key, value in instrument_mapping.items():
        inverted_mapping.setdefault(value, list()).append(key)
    return inverted_mapping


def find_stems(target_instruments, track_database, track_folder):
    stem_names = os.listdir(track_folder)
    instrument_stems = {}
    for target_instrument in target_instruments:
        instrument_stems[target_instrument] = []
    other_stems = []

    inverted_mapping = track_database.get_inverted_mapping()
    for stem_name in stem_names:
        is_audio_file, extension = is_accepted_audio_file(stem_name)
        if not is_audio_file:
            print('Found file extension {0}, ignoring'.format(extension))
            continue

        is_target = False
        for target_instrument, instruments in inverted_mapping.items():
            if target_instrument not in target_instruments:
                continue
            is_instrument = False
            for instrument in instruments:
                if instrument in utils.normalize_stem_name(stem_name.lower()):
                    is_instrument = True
                    is_target = True
                    break

            if is_instrument:
                instrument_stems[target_instrument].append(stem_name)
                break

        if not is_target:
            other_stems.append(stem_name)

    return instrument_stems, other_stems


def present_and_modify_stems(instrument_stems, other_stems):
    all_correct = False
    indexed_instruments = [i for i in instrument_stems.keys()]
    while not all_correct:
        stem_index = 1
        indexed_stems = []
        for target_instrument, target_stems in instrument_stems.items():
            instrument_index = indexed_instruments.index(target_instrument)
            print('\nPotential {0} ({1}) stems:'.format(target_instrument, instrument_index))
            for target_stem in target_stems:
                print('{0}) {1}'.format(stem_index, target_stem))
                indexed_stems.append(target_stem)
                stem_index += 1

        print('\nOther stems:')
        for other_stem in other_stems:
            print('{0}) {1}'.format(stem_index, other_stem))
            indexed_stems.append(other_stem)
            stem_index += 1

        user_input = input('\nInstructions:\n'
                           '- stem index + group name or group index to move stem (\'3 piano\', \'3 1\')\n'
                           '- stem index without group to move to other (\'3\')\n'
                           '- empty if all correct\n'
                           'What to do? ').split()
        if len(user_input) == 0:
            all_correct = True
        else:
            switched_index = int(user_input[0]) - 1
            if len(user_input) > 1:
                if user_input[1].isdigit():
                    new_group = indexed_instruments[int(user_input[1])]
                else:
                    new_group = user_input[1]
            else:
                new_group = 'other'

            stem_to_switch = indexed_stems[switched_index]
            old_list = None
            for _, stems in instrument_stems.items():
                if stem_to_switch in stems:
                    old_list = stems
                    break
            if old_list is None:
                old_list = other_stems

            new_list = other_stems if new_group == 'other' else instrument_stems.get(new_group, None)
            if new_list is None:
                print('\nNo group named {0} is known'.format(new_group))
            else:
                old_list.remove(stem_to_switch)
                new_list.append(stem_to_switch)


def build_stem_data(instrument_stems, other_stems, track_folder):
    stems = {}
    for target_instrument, target_stems in instrument_stems.items():
        for target_stem in target_stems:
            stems[target_stem] = {
                'instrument': target_instrument,
                'path': os.path.join(track_folder, target_stem)
            }
    for other_stem in other_stems:
        stems[other_stem] = {
            'instrument': 'other',
            'path': os.path.join(track_folder, other_stem)
        }
    return stems


def get_available_instruments(instrument_stems, other_stems):
    available_instruments = []
    for instrument, stems in instrument_stems.items():
        if len(stems) > 0:
            available_instruments.append(instrument)
    if len(other_stems) > 0:
        available_instruments.append('other')
    return available_instruments


def update_mappings(instrument_stems, track_database):
    for target_instrument, stem_names in instrument_stems.items():
        for stem_name in stem_names:
            track_database.add_mapping(utils.normalize_stem_name(stem_name), target_instrument)


def get_stems(target_instruments, track_database, track_folder):
    instrument_stems, other_stems = find_stems(target_instruments, track_database, track_folder)
    present_and_modify_stems(instrument_stems, other_stems)
    update_mappings(instrument_stems, track_database)
    stems = build_stem_data(instrument_stems, other_stems, track_folder)
    available_instruments = get_available_instruments(instrument_stems, other_stems)
    return available_instruments, stems
