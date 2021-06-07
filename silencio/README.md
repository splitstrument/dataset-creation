# silencio

This tool is used to detect the amount of silence in a track and optionally create new tracks where silence is cut out.
Tracks with a silence ratio below some given ratio can be adjusted, so the ratio fits some other ratio.

Silences at the beginning and end of files is preferred when cutting because they interfere the least with the structure
of the song. Adjusted tracks are exported to a separate folder as to not overwrite the source files.

# Parameters

| Option           | Description                                             | Required              | Default      | Example                                                                 |
|------------------|---------------------------------------------------------|-----------------------|--------------|-------------------------------------------------------------------------|
| --source-folder  | path to folder containing training data                 | X                     | -            | --source-folder D:\ba_data\trainingdatageneration\target\tracks_22050hz |
| --reduce-silence | whether to reduce silence in tracks by cutting them out |                       | False        | --reduce-silence true                                                   |
| --ratio-cutoff   | limit for ratio of silence to audible data to reduce    |                       | 30           | --ratio-cutoff 30                                                       |
| --target-ratio   | what ratio tracks should have after cutting             |                       | ratio-cutoff | --target-ratio 50                                                       |
| --target-folder  | path to to save tracks with reduced silence             | X (if reduce-silence) | -            | --target-folder D:\ba_data\trainingdatageneration\silencetarget         |