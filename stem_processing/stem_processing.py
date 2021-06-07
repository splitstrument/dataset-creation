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
parser.add_argument('--fft_window', default=1536, type=int, help='sample size of FFT windows')
parser.add_argument('--sample_rate', default=11025, type=int, help='target samplerate in Hz')
parser.add_argument('--mono', type=str2bool, default=False, help='treat audio as mono')
parser.add_argument('--generate_image', type=str2bool, default=False,
                    help='if spectrogram image should be generated and saved')
parser.add_argument('--job_count', default=multiprocessing.cpu_count(), type=int,
                    help='maximum number of concurrently running jobs')
parser.add_argument('--instrument', help='the instrument to create training data for', required=True)
parser.add_argument('--additional-instruments', default=[], nargs='*',
                    help='the instruments to to mix into the source instrument')
parser.add_argument('--generate_spectrograms', type=str2bool, default=False, help='generate spectrograms after mixing')
parser.add_argument('--check_quality', type=str2bool, default=True, help='check if quality markers exist')
parser.add_argument('--sample-rates', default=[], nargs='*', help='what additional sample rates should be created')

args = parser.parse_args()


def generate_container(file, destination, fft_window, target_sample_rate, mono, generate_image):
    global error_count
    try:
        audio, sample_rate = librosa.load(file, mono=mono,
                                          sr=target_sample_rate if target_sample_rate > 0 else None)
        spectrograms = []
        real_stereo = isinstance(audio[0], np.ndarray)
        if not mono and real_stereo:
            spectrograms.append(stft_to_complex_spectrogram(
                generate_spectrogram(destination, audio[0], '0-stereo_left', fft_window, sample_rate, generate_image)))
            spectrograms.append(stft_to_complex_spectrogram(
                generate_spectrogram(destination, audio[1], '1-stereo_right', fft_window, sample_rate, generate_image)))
        else:
            spectrograms.append(stft_to_complex_spectrogram(
                generate_spectrogram(os.path.basename(file), audio, '0-mono', fft_window, sample_rate, generate_image)))

        configuration = 'fft-window=%d_sample-rate=%d_channels=%d-%s' % (
            fft_window, sample_rate, 1 if mono else 2, 'mono' if mono else 'stereo')

        song = os.path.basename(os.path.dirname(file))
        collection = os.path.basename(os.path.dirname(os.path.dirname(file)))

        folder = os.path.join(destination, configuration, collection, song)
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except:
                pass
        path = os.path.join(folder, '%s-spectrogram_%s' % (os.path.basename(file), configuration))

        save_spectrogram_data(spectrograms, path, fft_window, sample_rate, mono, real_stereo, song, collection)
        print('Generated spectrogram %s' % path)
    except Exception as e:
        print('Error while generating spectrogram for %s: %s' % (file, str(e)))
        error_count += 1
        pass


def generate_spectrogram(name, audio, part, fft_window, sample_rate, generate_image):
    stft = librosa.stft(audio, fft_window)
    if generate_image:
        save_spectrogram_image(stft_to_real_spectrogram(stft), name, part, fft_window, sample_rate)
    return stft


def stft_to_real_spectrogram(stft):
    spectrogram = np.log1p(np.abs(stft))
    return np.array(spectrogram)[:, :, np.newaxis]


def stft_to_complex_spectrogram(stft):
    real_part = np.real(stft)
    imag_part = np.imag(stft)
    spectrogram = np.zeros((stft.shape[0], stft.shape[1], 2))
    spectrogram[:, :, 0] = real_part
    spectrogram[:, :, 1] = imag_part
    return spectrogram


def save_spectrogram_image(spectrogram, name, part, fft_window, sample_rate):
    file_name = '%s_spectrogram_%s_fft-window[%d]_sample-rate[%d].png' % (name, part, fft_window, sample_rate)
    real_part = spectrogram[:, :, 0]
    cm_hot = get_cmap('plasma')
    image = np.clip((real_part - np.min(real_part)) / (np.max(real_part) - np.min(real_part)), 0, 1)
    with warnings.catch_warnings():
        image = cm_hot(image)
        warnings.simplefilter('ignore')
        io.imsave(file_name, image)


def save_spectrogram_data(spectrograms, file, fft_window, sample_rate, mono, real_stereo, song, collection):
    h5f = h5py.File(file + '.h5', 'w')
    if len(spectrograms) > 1:
        h5f.create_dataset('spectrogram_left', data=spectrograms[0])
        h5f.create_dataset('spectrogram_right', data=spectrograms[1])
    else:
        h5f.create_dataset('spectrogram', data=spectrograms[0])
    dimensions = spectrograms[0].shape
    h5f.create_dataset('height', data=dimensions[0])
    h5f.create_dataset('width', data=dimensions[1])
    h5f.create_dataset('depth', data=dimensions[2])
    h5f.create_dataset('fft_window', data=fft_window)
    h5f.create_dataset('sample_rate', data=sample_rate)
    h5f.create_dataset('mono', data=mono)
    h5f.create_dataset('stereo', data=real_stereo)
    h5f.create_dataset('song', data=song)
    h5f.create_dataset('collection', data=collection)
    h5f.create_dataset('file', data=os.path.basename(file))
    h5f.close()


def build_destination(file, path, destination):
    return file.new_filename(path, destination)


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

if args.generate_spectrograms:
    print('\nGenerating spectrograms' % args.job_count)

    start = time.time()
    Parallel(n_jobs=args.job_count)(
        delayed(generate_container)(
            file,
            args.destination,
            args.fft_window,
            args.sample_rate,
            args.mono,
            args.generate_image
        ) for file in files)
    end = time.time()

    print('Finished generating spectrograms in %d [s] with %d errors' % ((end - start), error_count))

print('\nFinished processing')
