#!/usr/bin/python3
import argparse
from os.path import join, exists
from shutil import copyfile
import yaml
import sqlite3 as sql
import time

parser = argparse.ArgumentParser(description='Export metadata to the Kobo database.')
parser.add_argument('-v', dest='volumes', help='Ids of volumes to import to the Kobo device.', default=None, type=str, nargs='*')
parser.add_argument('-p', dest='path', help='Path to working directory.', default='./', type=str)
parser.add_argument('-k', dest='kobo', help='Name of Kobo device.', default='KOBORTIN', type=str)
parser.add_argument('-u', dest='user', help='Name of user.', default='mjacquet', type=str)
parser.add_argument('-s', dest='isos', help='Specify if the manga is a oneshot', action='store_true')
args = parser.parse_args()

def time_to_kobo(y, m, d, h=None, mi=None, s=None):
    y = str(y)
    m = str(m)
    d = str(d)
    if h is None: h = '00'
    else: h = str(h)
    if mi is None: mi = '00'
    else: mi = str(mi)
    if s is None: s = '00'
    else: s = str(s)
    return y + '-' + m + '-' + d + 'T' + h + ':' + mi + ':' + s + 'Z'

if __name__ == '__main__':
    device_path = '/media/'+args.user+'/'+args.kobo
    path = args.path

    # Load metadata
    with open(join(path,'.metadata.yaml'), 'r') as yamlfile:
        metadata = yaml.safe_load(yamlfile)
    serie = metadata['name']
    author = metadata['author']
    try:
        artist = metadata['artist']
        author = author + ', ' + artist
    except KeyError:
        artist = None
    volumes = metadata['volumes']
    editor = metadata['editor']
    language = metadata['language']
    description = '<div style="text-align: justify;">' + metadata['synopsis'] + '<div>'

    # Copy all requested files to the Kobo device
    for id in volumes:
        if args.volumes is not None and str(id) not in args.volumes:
            continue
        file = volumes[id]['file']
        if not exists(join(path,file)):
            print('Skipping: '+file+' does not exist.')
            continue
        if exists(join(device_path,'Mangas',file)):
            print('Skipping: '+file+' already exists on Kobo device.')
            continue
        print('Importing '+file)
        copyfile(join(path,file), join(device_path,'Mangas',file))

    # Ask for user to initialize the new files in database by disconnecting Kobo, and plug it back
    read = input('All desired files has been copied on the Kobo device.\n' +
                 'Please unplug it and wait for the end of the importation, and plug it back.\n' +
                 'Press any key when the Kobo device is plugged again and detected by the computer.')

    # Connect to Kobo database
    db = sql.connect(join(device_path,'.kobo/KoboReader.sqlite'))
    c = db.cursor()

    # Get system time and convert it to kobo time format
    t = time.localtime()
    t_kobo = time_to_kobo(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

    # Remove existing collection with this name if any and create a new one
    if not args.isos:
        c.execute("DELETE FROM Shelf WHERE InternalName='"+serie+"'")
        c.execute("DELETE FROM ShelfContent WHERE ShelfName='"+serie+"'")
        c.execute("INSERT INTO Shelf VALUES (?,?,?,?,?,?,?,?,?,?,?) ", (t_kobo, serie, serie, t_kobo, serie, None, 'false', 'true', 'false', None, None))

    # Import all the metadatas to the Kobo database
    for id in volumes:
        if not args.isos:
            if args.volumes is not None and str(id) not in args.volumes:
                continue
            # Get volume metadata
            vol = volumes[id]
            file = vol['file']
            contentID =  join('file:///mnt/onboard/Mangas',file)
            title = vol['name']
            try:
                original_title = vol['original']
                title = title + ' (' + original_title + ')'
            except KeyError:
                original_title = None
            try:
                (d,m,y) = vol['date'].split('-')
                date = time_to_kobo(y,m,d)
            except KeyError:
                date = None
        else:
            title = serie
            vol = volumes[1]
            file = vol['file']
            contentID =  join('file:///mnt/onboard/Mangas',file)
            try:
                (d,m,y) = vol['date'].split('-')
                date = time_to_kobo(y,m,d)
            except KeyError:
                date = None
            try:
                original_title = metadata['original']
                title = title + ' (' + original_title + ')'
            except KeyError:
                original_title = None

        print('Treating '+file)

        c.execute("UPDATE content SET Attribution=?  WHERE ContentID=?" , (author,      contentID))
        c.execute("UPDATE content SET Title=?        WHERE ContentID=?" , (title,       contentID))
        c.execute("UPDATE content SET Publisher=?    WHERE ContentID=?" , (editor,      contentID))
        c.execute("UPDATE content SET Language=?     WHERE ContentID=?" , (language,    contentID))
        c.execute("UPDATE content SET Description=?  WHERE ContentID=?" , (description, contentID))
        if not args.isos:
            c.execute("UPDATE content SET Series=?       WHERE ContentID=?" , (serie,       contentID))
            c.execute("UPDATE content SET SeriesNumber=? WHERE ContentID=?" , (id,          contentID))
        if date is not None:
            c.execute("UPDATE content SET DateCreated=?  WHERE ContentID=?" , (date,        contentID))

        c.execute("INSERT INTO ShelfContent VALUES (?,?,?,'false','false')", (serie, contentID, t_kobo))

    db.commit()
    db.close()