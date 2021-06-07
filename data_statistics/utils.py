import os
import re


def normalize_instrument_name(instrument):
    instrument = instrument.lower()
    instrument = instrument.replace('(continued)', '')
    instrument = instrument.strip()
    return instrument


def normalize_stem_name(stem):
    stem, _ = os.path.splitext(stem)
    search = re.search(r'[0-9_]*([A-Za-z_\-+ ]+)[0-9]*', stem)
    if search is not None:
        groups = search.groups()
        if len(groups) > 1:
            stem = groups[1]
    return normalize_instrument_name(stem)
