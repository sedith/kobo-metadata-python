# metadata-kobo-python

Exports the metadata from a customized yaml file to the Kobo database.  
Written for Linux (access path to Kobo device begin `/media/<user>/<device>`). Needs to be adapted for any other OS.

## Dependencies

* python3
* pyyaml

## Metadata file

The metadata are stored in a yaml file called _.metadata.yaml_. The script `init_metadata` creates a skeleton for such a file.

The fiels that are exported to the Kobo are :
* name
* author
* editor
* language
* synopsis
* volume ID, name, and date (_dd-mm-yyyy_ or _yyyy_)

Set to None

Any additional field will be ignored when exporting be can be managed by the user.
The file name associated to each _volume_ entry is required.

## Exporting to the Kobo device

The export scripts first copies all the files to the Kobo, then (once the Kobo processed each file), update the metadatas.

The export script requires parameters:
* the name of the Kobo device
* the user name to access the device in `/media/`
* the path to the folder containing the files to export (default `.`)
* the directory name on the Kobo device
* the `isos` flag, specifying if the upload is a one shot or a serie

The metadata file and all the files to be uploaded are assumed to be in the same folder.  
For a serie, a Kobo collection is created when uploading the metadata. If the same serie was previously on the device, it is deleted are created again with the new values.  
