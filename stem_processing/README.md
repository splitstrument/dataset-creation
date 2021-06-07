# stem_processing

This is an adjusted version of the `trainingdata_generator` from https://github.com/unmix-io/tools.

The following adjustements were made:
* updates for newer versions of libraries
* replace handling of boolean command line arguments
* check for markers from our `quality_tool` to exclude tracks with poor quality
* mix stems for instruments that consist of multiple stems
  * 'mix' and 'excluded' stems are ignored
* adjust folder handling and copy used music files to destination for clear separation of data
* allow generation of multiple different versions with different sample rates

## Parameters

| Option                   | Description                                          | Required | Default                     | Example                                          |
|--------------------------|------------------------------------------------------|----------|-----------------------------|--------------------------------------------------|
| --path                   | path to source files                                 | X        | -                           | --path=D:\ba_data\concept                        |
| --destination            | path to create data format files                     | X        | -                           | --destination=D:\ba_data\concept_training        |
| --fft_window             | sample size of FFT windows                           |          | 1536                        | --fft_window=1536                                |
| --sample_rate            | target samplerate in Hz                              |          | 11025                       | --sample_rate=11025                              |
| --mono                   | treat audio as mono                                  |          | False                       | --mono false                                     |
| --generate_image         | if spectrogram image should be generated and saved   |          | False                       | --generate_image false                           |
| --job_count              | maximum number of concurrently running jobs          |          | multiprocessing.cpu_count() | --job_count=4                                    |
| --instrument             | the instrument to create training data for           | X        | -                           | --instrument=vocals                              |
| --additional-instruments | the instruments to to mix into the source instrument |          | -                           | --additional-instruments distorted_guitar vocals |
| --generate_spectrograms  | generate spectrograms after mixing                   |          | False                       | --generate_spectrograms false                    |
| --check_quality          | check if quality markers exist                       |          | True                        | --check_quality true                             |
| --sample-rates           | what additional sample rates should be created       |          | -                           | --sample-rates 22050                             |