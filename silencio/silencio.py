import os
import argparse
import sys
from helperutils.boolean_argparse import str2bool
import silence_detector
import silence_cutter

parser = argparse.ArgumentParser(description='Check amount of silence and ratio to audible data in tracks')
parser.add_argument('--source-folder', required=True, help='path to folder containing training data')
parser.add_argument('--reduce-silence', type=str2bool, default=False,
                    help='whether to reduce silence in tracks by cutting them out')
parser.add_argument('--ratio-cutoff', type=int, default=30, help='limit for ratio of silence to audible data to reduce')
parser.add_argument('--target-ratio', type=int, help='what ratio tracks should have after cutting')
parser.add_argument('--min-ratio', default=0, type=int, help='what ratio adjusted tracks have to reach or be removed from dataset')
parser.add_argument('--target-folder', help='path to to save tracks with reduced silence')
args = parser.parse_args()

if not os.path.isdir(args.source_folder):
    sys.exit('Provided path to tracks is not a folder')

if args.reduce_silence and not os.path.isdir(args.target_folder):
    sys.exit('Provided path to target is not a folder')

if args.target_ratio is None:
    args.target_ratio = args.ratio_cutoff

track_ratios = silence_detector.find_silences(args.source_folder)
if args.reduce_silence:
    silence_cutter.cut_silence(track_ratios, args.ratio_cutoff, args.target_ratio, args.min_ratio, args.target_folder)
