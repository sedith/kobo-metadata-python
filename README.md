# metadata-kobo-python

Exports the metadata from a customized yaml file to the Kobo database.  
Written for Linux (access path to Kobo device begin `/media/<user>/<device>`). Needs to be adapted for any other OS.

This package is partially based on [Akkana's scripts for Kobo](https://github.com/akkana/scripts/tree/master/kobo) for a couple of functions in `utils.py`.

## Dependencies

* python3

## Metadata file

The metadata are stored in a yaml file called _.metadata.yaml_. The script `init_metadata` creates a skeleton for such a file.

The fiels that are exported to the Kobo are :
* name
* author (attribution)
* editor (publisher)
* language
* synopsis (description)
* volume ID, name, and date (_dd-mm-yyyy_, _mm-yyyy_ or _yyyy_)

Any additional field will be ignored when exporting, but can be managed by the user.
The file name associated to each _volume_ entry is required.

## Exporting to the Kobo device

The export scripts first copies all the files to the Kobo, then (once the Kobo processed each file), update the metadatas.
This requires manual plug/unplug of the Kobo device.

The export script requires parameters:
* the path to the Kobo device
* the path to the folder containing the files to export (default `.`)
* the directory name on the Kobo device
