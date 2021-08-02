#!/usr/bin/python3
import zipfile
from os.path import basename, join
import bs4


class EpubMeta:
    """Data representation and manipulation of the epub metadata.
    Mandatory fields: name, author, publisher, date, lang, synopsis
    Optional fields: serie, vol, ISBN
    """

    epub_fields = {'name': 'dc:title', 'author': 'dc:creator', 'publisher': 'dc:publisher', 'date': 'dc:date'}

    def __init__(self, filename, path='.'):
        self.path = path
        self.filename = filename
        self.zip = None
        self.opf = None
        self.soup = None

    def load_epub(self):
        """Load the epub file and parse the OPF content."""
        # Read the epub (zip) archive
        self.zip = zipfile.ZipFile(join(self.path, self.filename))

        # Find the opf file in the epub archive
        content = None
        for f in self.zip.namelist():
            if basename(f).endswith('.opf'):
                self.opf = f
                content = self.zip.open(f)
                break

        # Parse xml file
        self.soup = bs4.BeautifulSoup(content, 'xml')
        content.close()

    def get_version(self):
        """Return the epub version (2 or 3)."""
        version_str = self.soup.package['version']
        return int(float(version_str))

    def get_field(self, key):
        """Find a given field in the OPF."""
        delete_tags = False
        elements = self.soup.getElementsByTagName(key)
        parent = None
        matches = []
        for el in elements:
            if not parent:
                parents = el.parentNode
            else:
                assert parent == parentNode
            if delete_tags:
                if el.childNodes:
                    print("Deleting:", el.childNodes[0].wholeText)
                else:
                    print("Deleting empty", key, "tag")
                el.parentNode.removeChild(el)

            elif el.childNodes:
                wholetext = el.childNodes[0].wholeText
                if type(wholetext) is not str:
                    wholetext = wholetext.encode('utf-8', 'backslashreplace')
                matches.append(wholetext)
            else:
                print("Empty", key, "tag")

        return matches, elements, parent
