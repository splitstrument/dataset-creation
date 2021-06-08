# data-statistics

Used to parse metadata and gather information on different datasets. Currently, MedleyDB, Slakh, Cambridge Music
Technology and Rockband / Guitar Hero are supported.
Instruments are mapped to instrument groups (e.g. 'Acoustic clean guitar' gets mapped to 'guitar'), with the mapping
being saved into a file called `mapping.yaml`.

For a basic overview about different available instruments, the number of tracks with piano, guitar and distorted guitar
is displayed.

For each unique combination of parameters passed to the tool, a YAML file with all the parsed metadata is created. This
means statistics can be calculated more quickly if that file already exists, since metadata will not be parsed again.
If additional tracks are found for an existing file, they are added to the file.

When dealing with Cambridge or Rockband / Guitar Hero data, an interactive prompt allows the grouping of stems to an
instrument. Mappings are updated on the fly, so similarly named stems will be more easily detected.

# Parameters for `statistics.py`

| Option               | Description                                           | Default | Example                                     |
|----------------------|-------------------------------------------------------|---------|---------------------------------------------|
| --slakh-path         | path to the root folder of the Slakh dataset          | -       | --slakh-path=D:\ba_data\slakh2100           |
| --medleydb-path      | path to the root folder of the MedleyDB dataset       | -       | --medleydb-path=D:\ba_data\MedleyDB         |
| --cambridge-path     | path to Cambridge data source                         | -       | --cambridge-path=D:\ba_data\cambridge       |
| --rockband-path      | path to Rockband data source                          | -       | --rockband-path=D:\ba_data\rockband         |
| --target-instruments | instruments to look for in Cambridge or Rockband data | -       | --target-instruments piano distorted_guitar |
| --save-frequency     | how often to save entered data to files               | 10      | --save-frequency=10                         |
| --tracks-filename    | the name of the file to write data to                 | -       | --tracks-filename=tracks.yaml               |

# Metadata

The folder `metadata` contains two tracks files for stems from Rockband / Guitar Hero and Cambridge Music Technology.
These can be used if you don't want to label them by yourself. Check the
[thesis paper](https://github.com/splitstrument/report) on where these stems came from. You will probably need to adjust
the paths in these files to match your system.
