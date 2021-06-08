import os
import h5py
import time
import librosa
import soundfile
import warnings
import argparse
import numpy as np
import multiprocessing
from skimage import io
from joblib import Parallel, delayed
from matplotlib.cm import get_cmap
from pydub import AudioSegment
from helperutils.boolean_argparse import str2bool
from datetime import datetime

error_count = 0

parser = argparse.ArgumentParser(
    description='Create hierarchical data format files including complex frequency spectrograms')
parser.add_argument('--path', help='path to source files', required=True)
parser.add_argument('--destination', help='path to create data format files', required=True)
parser.add_argument('--mono', type=str2bool, default=False, help='treat audio as mono')
parser.add_argument('--job_count', default=multiprocessing.cpu_count(), type=int,
                    help='maximum number of concurrently running jobs')
parser.add_argument('--instrument', help='the instrument to create training data for', required=True)
parser.add_argument('--additional-instruments', default=[], nargs='*',
                    help='the instruments to to mix into the source instrument')
parser.add_argument('--check_quality', type=str2bool, default=True, help='check if quality markers exist')
parser.add_argument('--sample-rates', default=[], nargs='*', help='what additional sample rates should be created')

args = parser.parse_args()

exclusion_properties = ['missing', 'inaudible', 'bad_quality', 'bleed', 'mislabeled']
necessary_properties = ['checked']


def is_quality_checked(instrument, root):
    for necessary_property in necessary_properties:
        if not os.path.isfile(os.path.join(root, '{0}_{1}'.format(instrument, necessary_property))):
            return False
    for exclusion_property in exclusion_properties:
        if os.path.isfile(os.path.join(root, '{0}_{1}'.format(instrument, exclusion_property))):
            return False
    return True


def mix_stems(destination, name, instrument, sources):
    tracks_folder = os.path.join(destination, 'tracks_44100hz')
    if not os.path.isdir(tracks_folder):
        os.mkdir(tracks_folder)
    target_path = os.path.join(tracks_folder, name)
    if not os.path.isdir(target_path):
        os.mkdir(target_path)
    filename = os.path.join(target_path, '{0}_{1}.wav'.format(instrument, name))

    if os.path.isfile(filename):
        return filename

    combined = None
    for source in sources:
        if combined is None:
            combined = AudioSegment.from_file_using_temporary_files(source)
        else:
            sound = AudioSegment.from_file_using_temporary_files(source)
            # len(audiosegment) returns milliseconds, so a difference up to 2 seconds is still fine
            if abs(len(sound) - len(combined)) > 2000:
                print('Lengths of stems are not all equal for track {0}, please check by hand'.format(filename))
            combined = combined.overlay(sound)

    if combined is not None:
        combined = combined.set_frame_rate(44100)
        combined.export(filename, format='wav', )
        current_time = datetime.now().strftime("%H:%M:%S")
        print('{0}: Exported \'{1}\' stem for track {2}'.format(current_time, instrument, name))
        return filename
    else:
        return None


def resample_track(sample_rate, folder, file, mono):
    track_folder = os.path.join(folder, os.path.basename(os.path.dirname(file)))
    if not os.path.isdir(track_folder):
        os.makedirs(track_folder, exist_ok=True)
    new_filename = os.path.join(track_folder, os.path.basename(file))
    if not os.path.isfile(new_filename):
        audio, old_sample_rate = librosa.load(file, mono=mono)
        librosa.resample(audio, old_sample_rate, sample_rate)
        soundfile.write(new_filename, audio, sample_rate)
        current_time = datetime.now().strftime("%H:%M:%S")
        print('{0}: Resampled track {1}'.format(current_time, file))


target_instruments = args.additional_instruments
target_instruments.append(args.instrument)

files = []  # Load all files into list
print('Loading and mixing music files')
for track in os.listdir(args.path):
    track_path = os.path.join(args.path, track)
    if not args.check_quality or is_quality_checked(args.instrument, track_path):
        instrument_stem_sources = []
        for target_instrument in target_instruments:
            additional_instrument_stem_path = os.path.join(track_path, target_instrument)
            if os.path.isdir(additional_instrument_stem_path):
                additional_stems = os.listdir(additional_instrument_stem_path)
                instrument_stem_sources += [os.path.join(additional_instrument_stem_path, s) for s in additional_stems]
        instrument_result = mix_stems(args.destination, track, 'instrument', instrument_stem_sources)
        if instrument_result is not None:
            files.append(instrument_result)

        other_stem_sources = []
        other_stems = [d for d in os.listdir(track_path) if
                       d not in target_instruments and d != 'mix' and d != 'excluded']
        for other_stem in other_stems:
            other_stem_path = os.path.join(track_path, other_stem)
            if os.path.isdir(other_stem_path):
                other_stem_sources += [os.path.join(other_stem_path, s) for s in os.listdir(other_stem_path)]
        song_stem_path = os.path.join(track_path, 'mix', 'song.ogg')
        if os.path.isfile(song_stem_path):
            other_stem_sources.append(song_stem_path)
        other_result = mix_stems(args.destination, track, 'rest', other_stem_sources)
        if other_result is not None:
            files.append(other_result)

print('\nFound %d music files' % len(files))

for sample_rate in args.sample_rates:
    print('\nResampling to {0}hz'.format(sample_rate))
    sample_rate = int(sample_rate)
    new_foldername = os.path.join(args.destination, 'tracks_{0}hz'.format(sample_rate))
    new_foldername = os.path.abspath(new_foldername)
    if not os.path.isdir(new_foldername):
        os.mkdir(new_foldername)

    start = time.time()
    Parallel(n_jobs=args.job_count)(
        delayed(resample_track)(
            sample_rate,
            new_foldername,
            file,
            args.mono
        ) for file in files)
    end = time.time()

    print('Finished resampling in {0} seconds'.format(end - start))

print('\nFinished processing')
