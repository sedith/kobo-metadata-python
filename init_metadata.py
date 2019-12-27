#!/usr/bin/python3
import argparse
from os import listdir, rename, getcwd
from os.path import isfile, isdir, join, exists
import re
import yaml

parser = argparse.ArgumentParser(description='Initialize metadata file for a given serie folder.')
parser.add_argument('-p', dest='path', help='Path to working directory.', default=None, type=str)
parser.add_argument('-s', dest='serie', help='Serie\'s name.', default=None, type=str)
parser.add_argument('-i', dest='index', help='Index of the first volume in the folder.', default=1, type=int)
# parser.add_argument('-a', dest='author', help='Author\'s name.', default=None, type=str)
args = parser.parse_args()

def sorted_aphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(data, key=alphanum_key)

def get_serie(path):
    serie = path.split('/')[-1]
    if serie == '': serie = path.split('/')[-2]
    return serie

def init_yaml(file, serie):
    file.write('--- # '+serie+' Metadata\n')

def write_yaml(file, key, value, n_indent=0, isoneliner=False):
    indent = '    ' * n_indent
    string = indent + key + ':'
    if not isoneliner: string += '\n'
    if value is not None: string += (indent+' ')*(not isoneliner) + '   ' + value + '\n'
    file.write(string)

if __name__ == '__main__':
    path = args.path
    if path is None: path = getcwd()

    serie = args.serie
    if serie is None: serie = get_serie(path);

    # author = args.author
    # if author is None: author = 'TODO'

    with open(join(path,'.metadata.yaml'), 'w') as yamlfile:
        init_yaml(yamlfile, serie)
        write_yaml(yamlfile, 'name', serie)
        write_yaml(yamlfile, 'author', 'TODO')
        write_yaml(yamlfile, 'editor', 'TODO')
        write_yaml(yamlfile, 'language', 'TODO')
        write_yaml(yamlfile, 'synopsis', 'TODO')
        write_yaml(yamlfile, 'volumes', None)

        cbz = sorted_aphanumeric([f for f in listdir(path)
                                    if isfile(join(path, f))
                                    and (f.lower().endswith('.cbz'))])
        i = args.index
        for file in cbz:
            (name,ext) = file.split('.')
            write_yaml(yamlfile, str(i), None, 1)
            write_yaml(yamlfile, 'name', name, 2, True)
            write_yaml(yamlfile, 'date', 'TODO', 2, True)
            write_yaml(yamlfile, 'file', file, 2, True)
            i += 1
