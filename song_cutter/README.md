# song_cutter

A simple tool to cut long files into smaller pieces to make them easier to handle. This was used to cut huge compilations
of solo instrument playing into 3-minute tracks for our pure dataset while training.

## Parameters for `song_cutter.py`

| Option           | Description                          | Required | Example                                |
|------------------|--------------------------------------|----------|----------------------------------------|
| --source-folder  | path to folder containing long files | X        | --source-folder /data/ba2/compilations |
| --save-to-folder | path to folder to save cut songs     | X        | --save-to-folder /data/ba2/pure        |
| --length         | desired song length in seconds       | X        | --length 180                           |