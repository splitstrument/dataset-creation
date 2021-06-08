# stem_processing

This tool is used to generate final training data from stems. It checks for markers from our `quality_tool` to exclude
tracks with poor quality and mixes stems for instruments that consist of multiple stems. `mix` and `excluded` stems are
ignored. It can generate multiple different versions with different sample rates

## Parameters for `stem_processing.py`

| Option                   | Description                                          | Required | Default                     | Example                                          |
|--------------------------|------------------------------------------------------|----------|-----------------------------|--------------------------------------------------|
| --path                   | path to source files                                 | X        | -                           | --path=D:\ba_data\concept                        |
| --destination            | path to create data format files                     | X        | -                           | --destination=D:\ba_data\concept_training        |
| --mono                   | treat audio as mono                                  |          | False                       | --mono false                                     |
| --job_count              | maximum number of concurrently running jobs          |          | multiprocessing.cpu_count() | --job_count=4                                    |
| --instrument             | the instrument to create training data for           | X        | -                           | --instrument=vocals                              |
| --additional-instruments | the instruments to to mix into the source instrument |          | -                           | --additional-instruments distorted_guitar vocals |
| --check_quality          | check if quality markers exist                       |          | True                        | --check_quality true                             |
| --sample-rates           | what additional sample rates should be created       |          | -                           | --sample-rates 22050                             |