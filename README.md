# Dataset creation

![ZHAW Logo](zhaw_logo.png)

Each tool is contained in its own folder, although they may act on the same data and sometimes exchange information
through YAML files. A short description for each tool follows, check the individual README files to further information.

* cambridge_genre_filter
  * used to analyze what genres the used tracks from Cambridge MT are
* data_organizer
  * used to move tracks into a uniform folder structure
* data_statistics
  * used to load information about different tracks
* quality_tool
  * used to check the quality of stems by hand before using them for training
* silencio
  * used to detect and remove silence in tracks for better training quality
* stem_processing
  * used to mix and resample stems into training data
* song_cutter
  * used to cut long compilations into smaller tracks that are easier to handle
  
Be sure to check our [utils repository](https://github.com/splitstrument/utils) for additional code that is needed.