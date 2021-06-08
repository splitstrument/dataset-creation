# data-organizer
This tool is used to move all files from different datasets to a single uniform data structure.

Stems will be grouped into folders for different instruments. Check the `mapping.yaml` file in the `data-statistics`
tool for an overview on what instrument groups exist. At this point in time many instruments are simply grouped into an
folder called `other`.

Note that any pre-mixed track will be moved into an instrument folder called `mix`.

## Example folder structure
```
root
+-- track1
|   +-- instrument1
|       +-- stem1.flac
|       +-- stem3.flac
|   +-- instrument2
|       +-- stem2.flac
|       +-- stem4.flac
|   +-- mix
|       +-- mix.flac
+-- track2
|   +-- instrument3
|       +-- stem1.wav
|   +-- instrument4
|       +-- stem2.wav
|       +-- stem4.wav
|   +-- mix
|       +-- mix.wav
```

## Parameters for `organizer.py`

| Option                 | Description                                                           | Required | Default     | Example                             |
|------------------------|-----------------------------------------------------------------------|----------|-------------|-------------------------------------|
| --tracks               | name of the file containing the track information                     |          | tracks.yaml | --tracks=tracks.yaml                |
| --destination          | path of the root folder where the tracks should be copied to          | X        | -           | --destination=D:\ba_data\test       |
| --copy-limit           | how many tracks to handle at most, mainly used for testing            |          | ∞           | --track-limit=2                     |
| --destructive-move     | moves tracks instead of copying them, changing the original dataset   |          | False       | --destructive-move false            |
| --required instruments | only move tracks that have at least one stem of all given instruments |          | -           | --required-instruments guitar piano |