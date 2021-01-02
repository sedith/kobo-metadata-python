#!/usr/bin/python3
from .utils import *
import yaml


def yaml_field(key, value, n_indent=0, is_oneliner=False, is_multiline=False):
    """Format a string for a yaml field.
    is_oneliner remove the linebreak after the field name;
    is_multiline adds a | after the field name to allow multiline value.
    The two fields are exclusives, but can both be False.
    """
    indent = '    ' * n_indent
    yaml_field = indent + key + ':'*(key != '-')
    if is_multiline: yaml_field += ' |\n'
    elif not is_oneliner: yaml_field += '\n'
    if value is not None:
        value = value.replace('\n', '\n'+'    '*is_multiline)
        value = value.replace('\n    \n','\n\n')    # fix empty tab from last line
        while value[-1] in ['\n', ' ']:
             value = value[:-1]    # remove last linebreak or spaces
        yaml_field += (indent+' ')*(not is_oneliner) + '   ' + value + '\n'
    return yaml_field

class CbzMeta:
    """Data representation and manipulation of the metadata yaml files for CBZ.
    Mandatory fields: name, author, editor, lang, synopsis, vol,
        vol.id, vol.id.name, vol.id.date, vol.id.file
    Optional fields: original, romanji, artist, credit.-.volumes/chapters,
        credit.-.from, credit.-.team, vol.id.original, vol.id.romanji

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
    editor:
        Hakusensha
    lang:
        en
    synopsis:
        Super synopsis.
    vol:
        1:
            name:   Oh-Roh
            date:   12-1989
            file:   Oh-Roh.cbz
            original:  王狼
        2:
            name:   Oh-Roh-Den
            date:   08-1990
            file:   Oh-Roh-Den.cbz
            original:  王狼伝
    """

    fields = ['name', 'original', 'romanji', 'author', 'artist', 'editor', 'lang', 'synopsis', 'credit', 'vol']
    vol_fields = ['name', 'date', 'file', 'original', 'romanji']
    credit_fields = ['chapters', 'volumes', 'from', 'team']

    def __init__(self, serie, path='.', filename='.metadata.yaml'):
        self.path = path
        self.filename = filename
        self.data = {'name':serie, 'author':'TODO', 'editor':'TODO', 'lang':'TODO', 'synopsis':'TODO', 'vol':None}

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

    def load_yaml(self):
        """Load the data from the yaml file."""
        with open(join(self.path,self.filename), 'r') as yamlfile:
            self.data = {**self.data, **yaml.safe_load(yamlfile)}

    def write_yaml(self):
        """Write or rewrite the data onto the yaml file."""
        with open(join(self.path,self.filename), 'w') as yamlfile:
            yamlfile.write('--- # %s Metadata\n' % self.data['name'])
            for key in self.fields:
                if key == 'vol':
                    yamlfile.write(yaml_field('vol', None))
                    if self.data['vol'] is None: continue
                    indices = sorted(self.data['vol'].keys())
                    for i_v in indices:
                        yamlfile.write(yaml_field(str(i_v), None, 1))
                        for key_v in self.vol_fields:
                            try:
                                value = self.data['vol'][i_v][key_v]
                                yamlfile.write(yaml_field(key_v, value, 2, is_oneliner=True))
                            except KeyError:
                                pass
                elif key == 'credit' and type(self.data['credit']) == list:
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
                        string = yaml_field(key, value, is_multiline=(key=='synopsis'))
                        yamlfile.write(string)
                    except KeyError:
                        pass

    def get_volumes_dict(self, index=1):
        """Scan the path and create the volumes field from the cbz files."""
        cbz = sorted_aphanumeric(self.path, ext=['cbz'])
        volumes = {}
        for file in cbz:
            (name,_) = file.split('.')
            volumes[i] = {'name':name, 'date':'TODO', 'file':file}
            i += 1
        self.set_field('vol', volumes)
