#!/usr/bin/python3
from .utils import sorted_aphanumeric
from os.path import join
import yaml


def yaml_field(key, value, n_indent=0, is_oneliner=False, is_multiline=False):
    """Format a string for a yaml field.
    is_oneliner remove the linebreak after the field name;
    is_multiline adds a | after the field name to allow multiline value.
    The two fields are exclusives, but can both be False.
    """
    indent = '    ' * n_indent
    yaml_field = indent + key + ':' * (key != '-')
    if is_multiline:
        yaml_field += ' |\n'
    elif not is_oneliner:
        yaml_field += '\n'
    if value is not None:
        value = value.replace('\n', '\n' + '    ' * is_multiline)
        value = value.replace('\n    \n', '\n\n')  # fix empty tab from last line
        while value[-1] in ['\n', ' ']:
            value = value[:-1]  # remove last linebreak or spaces
        yaml_field += (indent + ' ') * (not is_oneliner) + '   ' + value + '\n'
    return yaml_field


class CbzMeta:
    """Data representation and manipulation of the metadata yaml files for CBZ.
    Mandatory fields: name, author, publisher, lang, synopsis, vol,
        vol.id, vol.id.name, vol.id.date, vol.id.file
    Optional fields: original, romanji, artist, credit.vols/chap,
        credit.site, credit.team, credit.editor, credit.cleaner,
        credit.raw, credit.translate, vol.id.original, vol.id.romanji

    A typical yaml file for metadata is is:
    --- # Oh-Roh Metadata
    name:
        Oh-Roh
    original:
        王狼
    author:
        Buronson
    artist:
        Kentarō Miura
    publisher:
        Hakusenshapathpathpatpathpathh
    lang:
        en
    synopsis:
        Super synopsis.
    vol:
        1:
            name:   Oh-Roh
            original:  王狼
            date:   12-1989
            file:   Oh-Roh.cbz
        2:
            name:   Oh-Roh-Den
            original:  王狼伝
            date:   08-1990
            file:   Oh-Roh-Den.cbz
    """

    # Ordered list of fields for clean writing is a consistent order
    fields = ['name', 'original', 'romanji', 'author', 'artist', 'publisher', 'lang', 'synopsis', 'credit', 'vol']
    vol_fields = ['name', 'original', 'romanji', 'date', 'file']
    credit_fields = ['chap', 'vols', 'site', 'team', 'editor', 'cleaner', 'raw', 'translate']

    def __init__(self, filename='.metadata.yaml', path='.'):
        self.path = path
        self.filename = filename
        self.data = {'name': 'TODO', 'author': 'TODO', 'publisher': 'TODO', 'lang': 'TODO', 'synopsis': 'TODO', 'vol': None}

    # Metadata
    def get_field(self, key):
        """Read the value of a field.
        Nested keys are passed are key.subkey.
        """
        keys = key.split('.')
        if len(keys) == 1:
            return self.data[keys[0]]
        elif len(keys) == 2:
            return self.data[keys[0]][keys[1]]
        elif len(keys) == 3:
            return self.data[keys[0]][keys[1]][keys[2]]

    def set_field(self, key, value):
        """Update the value of a field.
        Nested keys are passed are key.subkey.
        """
        keys = key.split('.')
        if len(keys) == 1:
            self.data[keys[0]] = value
        elif len(keys) == 2:
            self.data[keys[0]][keys[1]] = value
        elif len(keys) == 3:
            self.data[keys[0]][keys[1]][keys[2]] = value

    # Interact with yaml file
    def load_yaml(self):
        """Load the data from the yaml file."""
        with open(join(self.path, self.filename), 'r') as yamlfile:
            self.data = {**self.data, **yaml.safe_load(yamlfile)}

    def write_yaml(self):
        """Write or rewrite the data onto the yaml file.

        I use this poorly written function instead of yaml.dump in order
        to control the yaml field orders and display style (oneline, multiline...)
        The way the credits are written is completely adhoc since there is no
        consistency on the information available regarding those. I decided to create an
        object for each set of volumes or chapters from one single team. When available,
        I also include the individual roles (cleaner, raw, trad...)
        """
        with open(join(self.path, self.filename), 'w') as yamlfile:
            yamlfile.write('--- # %s Metadata\n' % self.data['name'])
            for key in self.fields:
                if key == 'vol':
                    yamlfile.write(yaml_field('vol', None))
                    if self.data['vol'] is None:
                        continue
                    indices = sorted(self.data['vol'].keys())
                    for i_v in indices:
                        yamlfile.write(yaml_field(str(i_v), None, 1))
                        for key_v in self.vol_fields:
                            try:
                                value = self.data['vol'][i_v][key_v]
                                yamlfile.write(yaml_field(key_v, value, 2, is_oneliner=True))
                            except KeyError:
                                pass
                elif key == 'credit' and key in self.data and type(self.data[key]) == list:
                    yamlfile.write(yaml_field('credit', None))
                    for cred in self.data['credit']:
                        yamlfile.write(yaml_field('-', None, 1))
                        for key_c in self.credit_fields:
                            try:
                                value = cred[key_c]
                                yamlfile.write(yaml_field(key_c, str(value), 2, is_oneliner=True))
                            except KeyError:
                                pass
                else:
                    try:
                        value = self.data[key]
                        string = yaml_field(key, value, is_multiline=(key == 'synopsis'))
                        yamlfile.write(string)
                    except KeyError:
                        pass

    # Misc
    def get_volumes_dict(self, index=1):
        """Scan the path and create the volumes field from the cbz files."""
        cbz = sorted_aphanumeric(self.path, ext=['cbz'])
        volumes = {}
        for file in cbz:
            (name, _) = file.split('.')
            volumes[index] = {'name': name, 'date': 'TODO', 'file': file}
            index += 1
        return volumes
