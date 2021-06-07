import os
from helperutils.stemloader import StemLoader
from collections import defaultdict


def check_tracks(path, stem_loader):
    print('Checking track {0}'.format(path))
    for stem in os.listdir(path):
        if stem.startswith('instrument'):
            print('Checking stem {0}'.format(stem))
            return load_silence_ratio_stem(stem, path, stem_loader)


def load_silence_ratio_stem(stem, path, stem_loader):
    file_path = os.path.join(path, stem)
    stem = stem_loader.get_stem(file_path)
    silence = detect_silence(stem)
    stem_duration_ms = stem.duration_seconds * 1000
    ratio = silence / stem_duration_ms
    print('Duration: {0}, Silence: {1}, Ratio: {2}'.format(stem_duration_ms, silence, ratio * 100))
    return ratio * 100


def detect_silence(sound, silence_threshold=-50.0, chunk_size=1000):
    trim_ms = 0
    silence_ms = 0
    while trim_ms < len(sound):
        if sound[trim_ms:trim_ms + chunk_size].dBFS < silence_threshold:
            silence_ms += chunk_size
        trim_ms += chunk_size

    return silence_ms


def find_silences(source_folder):
    stem_loader = StemLoader()
    tracks = defaultdict(list)
    for track in os.listdir(source_folder):
        track_path = os.path.join(source_folder, track)
        if os.path.isdir(track_path):
            ratio = check_tracks(track_path, stem_loader)
            if ratio is not None:
                ratio_key = str(min(int(ratio / 10) * 10 + 10, 100))
                tracks[ratio_key].append((track_path, ratio))

    print('Songs with less than 10% silence: {0}'.format(len(tracks['10'])))
    print('Songs with less than 20% silence: {0}'.format(len(tracks['20'])))
    print('Songs with less than 30% silence: {0}'.format(len(tracks['30'])))
    print('Songs with less than 40% silence: {0}'.format(len(tracks['40'])))
    print('Songs with less than 50% silence: {0}'.format(len(tracks['50'])))
    print('Songs with less than 60% silence: {0}'.format(len(tracks['60'])))
    print('Songs with less than 70% silence: {0}'.format(len(tracks['70'])))
    print('Songs with less than 80% silence: {0}'.format(len(tracks['80'])))
    print('Songs with less than 90% silence: {0}'.format(len(tracks['90'])))
    print('Songs with more than 90% silence: {0}'.format(len(tracks['100'])))

    return tracks
