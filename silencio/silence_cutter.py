import os
import silence_detector
import shutil
from helperutils.stemloader import StemLoader

stem_loader = StemLoader()


def find_contiguous_silences(sound, silence_threshold=-50.0, chunk_size=1000):
    trim_ms = 0
    silences = []
    current_silence_start = None

    while trim_ms < len(sound):
        if sound[trim_ms:trim_ms + chunk_size].dBFS < silence_threshold:
            if current_silence_start is None:
                current_silence_start = trim_ms
        elif current_silence_start is not None:
            silences.append((current_silence_start, trim_ms + chunk_size))
            current_silence_start = None
        trim_ms += chunk_size

    if current_silence_start is not None:
        silences.append((current_silence_start, trim_ms + chunk_size))

    return silences


def calculate_silence_length(silence):
    return silence[1] - silence[0]


def find_silences_to_cut(sound_length, ratio, target_ratio, silences):
    current_silence_amount = sound_length / 100 * ratio
    max_silence_amount = sound_length - sound_length / 100 * target_ratio
    if current_silence_amount > max_silence_amount:
        silence_to_remove = current_silence_amount - max_silence_amount

        cuts = []

        if silence_to_remove > 0 and len(silences) > 0:
            current_cut_length = 0
            first_silence = silences[0]
            beginning_silence = first_silence if first_silence[0] <= 0 else None
            if beginning_silence is not None:
                cuts.append(beginning_silence)
                current_cut_length += calculate_silence_length(beginning_silence)

            last_silence = silences[-1]
            ending_silence = last_silence if len(silences) > 1 and last_silence[1] >= sound_length else None
            if current_cut_length < silence_to_remove and ending_silence is not None:
                cuts.append(ending_silence)
                current_cut_length += calculate_silence_length(ending_silence)

            middle_silences = silences[1:-1]
            middle_silences.sort(reverse=True, key=calculate_silence_length)
            while current_cut_length < silence_to_remove and len(middle_silences) > 0:
                next_silence = middle_silences.pop(0)
                cuts.append(next_silence)
                current_cut_length += calculate_silence_length(next_silence)

            if current_cut_length >= silence_to_remove:
                return cuts, True

        return cuts, False

    return None, False


def cut_stem(stem, cuts):
    source_sound = stem_loader.get_stem(stem)
    parts = []
    current_position = 0
    cuts.sort(key=lambda c: c[0])
    for cut in cuts:
        if cut[0] > 0:
            parts.append(source_sound[current_position:cut[0]])
        current_position = cut[1]

    if current_position < len(source_sound):
        parts.append(source_sound[current_position:])

    if len(parts) <= 0:
        parts.append(source_sound)

    target_sound = parts[0]
    for part in parts[1:]:
        target_sound += part

    return target_sound


def perform_cuts(instrument, rest, cuts, target_path, target_ratio, min_ratio):
    instrument_result = cut_stem(instrument, cuts)

    new_silence_length = silence_detector.detect_silence(instrument_result)
    new_silence_ratio = new_silence_length / len(instrument_result)
    instrument_target_path = os.path.join(target_path, os.path.basename(instrument))
    if new_silence_ratio > min_ratio / 100:
        print('Stem %s did not reach minimum ratio after cutting' % instrument_target_path)
    else:
        if new_silence_ratio > target_ratio / 100:
            print('Stem %s did not reach target ratio after cutting' % instrument_target_path)
        if not os.path.isdir(target_path):
            os.mkdir(target_path)
        instrument_result.export(instrument_target_path, format='wav')
        rest_target_path = os.path.join(target_path, os.path.basename(rest))
        cut_stem(rest, cuts).export(rest_target_path, format='wav')


def cut_track(ratio, target_folder, target_ratio, min_ratio, track):
    cuts = []
    ratio_reached = False
    instrument_stem = None
    rest_stem = None
    for stem in os.listdir(track):
        stem_path = os.path.join(track, stem)
        if stem.startswith('instrument'):
            instrument_stem = stem_path
            sound = stem_loader.get_stem(instrument_stem)
            silences = find_contiguous_silences(sound)
            cuts, ratio_reached = find_silences_to_cut(len(sound), ratio, target_ratio, silences)
        elif stem.startswith('rest'):
            rest_stem = stem_path

    if cuts is None:
        print('Cutting not necessary for track %s' % track)
        return

    if not ratio_reached:
        print('Could not find enough silences to cut in track %s' % track)

    track_path = os.path.join(target_folder, os.path.basename(track))
    perform_cuts(instrument_stem, rest_stem, cuts, track_path, target_ratio, min_ratio)


def cut_silence(track_ratios, ratio_cutoff, target_ratio, min_ratio, target_folder):
    for key, tracks in track_ratios.items():
        for track, ratio in tracks:
            if 100 - ratio < ratio_cutoff:
                cut_track(ratio, target_folder, target_ratio, min_ratio, track)
            else:
                target_track_folder = os.path.join(target_folder, os.path.basename(track))
                if not os.path.isdir(target_track_folder):
                    os.mkdir(target_track_folder)
                for stem in os.listdir(track):
                    stem_path = os.path.join(track, stem)
                    shutil.copy(stem_path, target_track_folder)
