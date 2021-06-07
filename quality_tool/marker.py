import os


class TrackMarker:
    is_missing = False
    has_bleed = False
    has_bad_quality = False
    is_inaudible = False
    is_audible = False
    is_mislabeled = False
    is_checked = False
    needs_detailed_check = False

    def __init__(self, track_path, instrument, cautious_mode=False):
        self.track_path = track_path
        self.instrument = instrument
        self.cautious_mode = cautious_mode
        self.read_all_marker_files()

    def mark_missing(self):
        if self.cautious_mode and self.is_missing:
            self.is_missing = False
            print('Unmarked as missing')
        else:
            self.is_missing = True
            print('Marked as missing')

    def mark_bleed(self):
        if self.cautious_mode and self.has_bleed:
            self.has_bleed = False
            print('Unmarked as having bleed')
        else:
            self.has_bleed = True
            print('Marked as having bleed')

    def mark_bad_quality(self):
        if self.cautious_mode and self.has_bad_quality:
            self.has_bad_quality = False
            print('Unmarked as having bad quality')
        else:
            self.has_bad_quality = True
            print('Marked as having bad quality')

    def mark_inaudible(self):
        if self.cautious_mode and self.is_inaudible:
            self.is_inaudible = False
            print('Unmarked as inaudible')
        else:
            self.is_inaudible = True
            print('Marked as inaudible')

    def mark_audible(self):
        if self.cautious_mode and self.is_audible:
            self.is_audible = False
            print('Unmarked as audible')
        else:
            self.is_audible = True
            print('Marked as audible')

    def mark_mislabeled(self):
        if self.cautious_mode and self.is_mislabeled:
            self.is_mislabeled = False
            print('Unmarked as mislabeled')
        else:
            self.is_mislabeled = True
            print('Marked as mislabeled')

    def mark_detailed(self):
        if self.cautious_mode and self.needs_detailed_check:
            self.needs_detailed_check = False
            print('Unmarked to check details')
        else:
            self.needs_detailed_check = True
            print('Marked to check details')

    def write_marks(self):
        if self.is_missing:
            self.write_marker_file('missing')
        if self.has_bleed:
            self.write_marker_file('bleed')
        if self.has_bad_quality:
            self.write_marker_file('bad_quality')
        if self.is_inaudible:
            self.write_marker_file('inaudible')
        if self.is_audible:
            self.write_marker_file('audible')
        if self.is_mislabeled:
            self.write_marker_file('mislabeled')
        if self.needs_detailed_check:
            self.write_marker_file('detailed')
        self.write_marker_file('checked')
        print('Marked track {0}'.format(self.track_path))

    def get_marks(self):
        return {
            'missing': self.is_missing,
            'bleed': self.has_bleed,
            'bad_quality': self.has_bad_quality,
            'inaudible': self.is_inaudible,
            'audible': self.is_audible,
            'mislabeled': self.is_mislabeled,
            'detailed': self.needs_detailed_check,
            'checked': True,
        }

    def write_marker_file(self, mark_name):
        marker_filepath = os.path.join(self.track_path, '{0}_{1}'.format(self.instrument, mark_name))
        if not os.path.isfile(marker_filepath):
            open(marker_filepath, 'w')

    def read_marker_file(self, mark_name):
        marker_filepath = os.path.join(self.track_path, '{0}_{1}'.format(self.instrument, mark_name))
        return os.path.isfile(marker_filepath)

    def read_all_marker_files(self):
        self.is_missing = self.read_marker_file('missing')
        self.has_bleed = self.read_marker_file('bleed')
        self.has_bad_quality = self.read_marker_file('bad_quality')
        self.is_inaudible = self.read_marker_file('inaudible')
        self.is_audible = self.read_marker_file('audible')
        self.is_mislabeled = self.read_marker_file('mislabeled')
        self.is_checked = self.read_marker_file('checked')
        self.needs_detailed_check = self.read_marker_file('detailed')

    def set_marks(self, marks):
        self.is_missing = marks['missing']
        self.has_bleed = marks['bleed']
        self.has_bad_quality = marks['bad_quality']
        self.is_inaudible = marks['inaudible']
        self.is_audible = marks['audible']
        self.is_mislabeled = marks['mislabeled']
        self.is_checked = marks['checked']
        self.needs_detailed_check = marks['detailed']
