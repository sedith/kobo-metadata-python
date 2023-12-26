import re
from os import listdir
from os.path import isfile, isdir, join, splitext


## misc
def sorted_aphanumeric(path, ext=[], ignore=[], dirs=False):
    """Alphanumeric sort all files in path.
    ext         -- extensions of files to consider, if applicable
    ignore      -- files to ignore
    dirs        -- list only directories
    """
    data = [
        f
        for f in listdir(path)
        if (
            ((not dirs and isfile(join(path, f))) or (dirs and isdir(join(path, f))))
            and f not in ignore
            and (ext == [] or get_ext(f.lower()) in ext)
        )
    ]
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)


def get_ext(file):
    """Return the extension of the given filename."""
    return splitext(file.lower())[1][1:]


def remove_ext(file):
    """Return the given filename without its extension."""
    return splitext(file.lower())[0]


## metadata
def get_volumes_dict(path, index=1):
    """Scan the path and create the volumes field from the cbz files."""
    cbz = sorted_aphanumeric(path, ext=['cbz'])
    volumes = {}
    for file in cbz:
        name = remove_ext(file)
        volumes[index] = {'name': name, 'date': 'TODO', 'file': file}
        index += 1
    return volumes
