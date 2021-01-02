#!/usr/bin/python3
from os import listdir
from os.path import isfile, isdir, join
import sqlite3 as sql
import time


def time_to_kobo(y, m, d='01', h='00', mi='00', s='00'):
    """Format timestamp for Kobo."""
    y = str(y)
    m = str(m)
    d = str(d)
    h = str(h)
    mi = str(mi)
    s = str(s)
    return y + '-' + m + '-' + d + 'T' + h + ':' + mi + ':' + s + 'Z'


class KoboDB:
    """Interact with Kobo database."""

    def __init__(self, path):
        self.path = path
        self.dbpath = None
        self.db = None
        self.cursor = None

    # Connexion
    def connect(self):
        """Create dbection handler with Kobo database."""
        dbpath = join(self.path, '.kobo/KoboReader.sqlite')
        self.db = sql.connect(dbpath)
        self.cursor = self.db.cursor()

    def disconnect(self):
        """Commit and close dbection to database."""
        self.db.commit()
        self.db.close()
        self.db = None
        self.cursor = None

    def get_current_time(self):
        """Get system time and format it for Kobo."""
        t = time.localtime()
        return time_to_kobo(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

    # Generic getters
    def get_fields(self, table='content'):
        """Get names of fields within a given table.
        PRAGMA table_info returns: (index, fieldname, type, None, 0)
        """
        self.cursor.execute('PRAGMA table_info(%s)' % table)
        return [field[1] for field in self.cursor.fetchall()]

    def get_list(self, table='content', selectors='*', modifiers='', order=''):
        """List elements within a given table.
        kwargs are:
        - selectors: list of fields to retrieve;
        - modifiers: list of OR conditions;
        - order: name of the ordering field.
        """
        # Format the sql request as:
        # SELECT [sel1,sel2] FROM [table] WHERE [mod1] AND mod2 ORDER BY [ord1]
        if selectors != '*':
            selectors = ','.join(selectors)
        if modifiers:
            modifiers = ' WHERE ' + ' OR '.join(modifiers)
        if order:
            order = ' ORDER BY %s' % order
            self.cursor.execute('SELECT %s FROM %s%s%s' % (selectors, table, modifiers, order))
        return self.cursor.fetchall()

    def get_list_dict(self, table='content', selectors='*', **kwargs):
        '''List elements within a given table as a dictionnary.'''
        l = self.get_list(table=table, selectors=selectors, **kwargs)
        if selectors == '*':
            selectors = self.get_field_names(table)
        return [dict(list(zip(selectors, values))) for values in l]

    # Book getters
    def book_from_title(self, bookname):
        """Fin a book contentID from its book title."""
        self.cursor.execute('SELECT ContentID FROM content WHERE Title=?', (bookname,))
        id = self.cursor.fetchone()
        if id:
            return id[0]

    def book_from_filename(self, filename):
        """Find a book contentID from its filename."""
        contentIDs = self.get_list('content', selectors=['ContentID'], modifiers=['BookID IS NULL'])
        for id in contentIDs:
            if id[0].endswith(filename):
                return id[0]

    # Manage books
    def list_books(self):
        """List all books in the database."""
        return self.get_list_dict('content', selectors=['Title'], modifiers=['BookID IS NULL'])

    def rm_book(self, contentID):
        """Remove a book and all its content from the database."""
        self.cursor.execute('DELETE FROM content WHERE ContentID=?', (contentID,))
        self.cursor.execute('DELETE FROM content WHERE BookID=?', (contentID,))

    def edit_book(self, contentID, bookname=None, author=None, publisher=None, lang=None, date=None, description=None, serie=None):
        """Edit a book from its contentID.
        the argument 'serie' should be a tuple (serieName, serieNumber)
        """
        if author:
            self.cursor.execute('UPDATE content SET Attribution=?  WHERE ContentID=?', (author, contentID))
        if bookname:
            self.cursor.execute('UPDATE content SET Title=?        WHERE ContentID=?', (bookname, contentID))
        if publisher:
            self.cursor.execute('UPDATE content SET Publisher=?    WHERE ContentID=?', (publisher, contentID))
        if lang:
            self.cursor.execute('UPDATE content SET Language=?     WHERE ContentID=?', (lang, contentID))
        if description:
            self.cursor.execute('UPDATE content SET Description=?  WHERE ContentID=?', (description, contentID))
        if date:
            self.cursor.execute('UPDATE content SET DateCreated=?  WHERE ContentID=?', (date, contentID))
        if serie:
            self.cursor.execute('UPDATE content SET Series=?       WHERE ContentID=?', (serie[0], contentID))
            self.cursor.execute('UPDATE content SET SeriesID=?     WHERE ContentID=?', (serie[0], contentID))
            self.cursor.execute('UPDATE content SET SeriesNumber=? WHERE ContentID=?', (serie[1], contentID))
            self.cursor.execute('UPDATE content SET SeriesNumberFloat=? WHERE ContentID=?', (serie[1], contentID))

    # Manage shelves
    def list_shelves(self):
        """List all shelves in the database."""
        return self.get_list_dict('Shelf', selectors=['Id'])

    def list_shelf_contents(self, shelfname):
        """List all books in a given shelf."""
        ids = self.get_list('ShelfContent', selectors=['contentID'], modifiers=['ShelfName="%s"' % shelfname])
        if ids != []:
            modifiers = ['ContentID="%s"' % id for id in ids]
            return self.get_list_dict('content', selectors=['Title'], modifiers=modifiers)

    def add_shelf(self, shelfname):
        """Create an empty shelf."""
        t = self.get_current_time()
        self.cursor.execute(
            'INSERT INTO Shelf VALUES (?,?,?,?,?,?,?,?,?,?,?) ', (t, shelfname, shelfname, t, shelfname, None, 'false', 'true', 'false', None, None)
        )

    def rm_shelf(self, shelfname):
        """Delte a shelf and all its content entries."""
        self.cursor.execute('DELETE FROM ShelfContent WHERE ShelfName=?', (shelfname,))
        self.cursor.execute('DELETE FROM Shelf WHERE Id=?', (shelfname,))

    def add_to_shelf(self, shelfname, contentID):
        """Add an book to a given shelf."""
        t = self.get_current_time()
        self.cursor.execute('INSERT INTO ShelfContent VALUES (?,?,?,?,?)', (shelfname, contentID, t, 'false', 'false'))
        self.cursor.execute('UPDATE Shelf SET LastModified=? WHERE Id=?', (t, shelfname))
