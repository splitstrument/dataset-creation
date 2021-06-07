import os
import yaml


def invert_mapping(instrument_mapping):
    inverted_mapping = dict()
    for key, value in instrument_mapping.items():
        inverted_mapping.setdefault(value, list()).append(key)
    return inverted_mapping


class TrackDatabase:
    unsaved_tracks = 0
    known_tracks = []

    def __init__(self, tracks_filepath, mapping_filepath, save_frequency=10):
        self.mapping_filepath = mapping_filepath
        if os.path.isfile(mapping_filepath):
            with open(mapping_filepath) as mapping_file:
                self.instrument_mapping = yaml.load(mapping_file, Loader=yaml.FullLoader)
        else:
            self.instrument_mapping = {}
        self.inverted_mapping = invert_mapping(self.instrument_mapping)

        self.tracks_filepath = tracks_filepath
        if os.path.isfile(tracks_filepath):
            with open(tracks_filepath) as tracks_file:
                self.tracks = yaml.load(tracks_file, Loader=yaml.FullLoader)
                for track in self.tracks:
                    self.known_tracks.append(track['name'])
        else:
            self.tracks = []

        self.save_frequency = save_frequency

    def track_known(self, track_name):
        return track_name in self.known_tracks

    def save_track(self, track):
        self.tracks.append(track)
        self.known_tracks.append(track['name'])
        self.unsaved_tracks += 1
        if self.unsaved_tracks >= self.save_frequency:
            self.save()
            self.unsaved_tracks = 0

    def save(self):
        with open(self.tracks_filepath, 'w') as tracks_file:
            yaml.dump(self.tracks, tracks_file)
        with open(self.mapping_filepath, 'w') as mapping_file:
            yaml.dump(self.instrument_mapping, mapping_file)

    def get_tracks(self):
        return self.tracks

    def add_mapping(self, source, target):
        self.instrument_mapping[source] = target
        self.inverted_mapping.setdefault(target, list()).append(source)

    def get_instrument_mapping(self):
        return self.instrument_mapping

    def get_inverted_mapping(self):
        return self.inverted_mapping
