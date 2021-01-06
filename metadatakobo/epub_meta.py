#!/usr/bin/python3
import zipfile

class EpubMeta:
    """Data representation and manipulation of the epub metadata."""

    def __init__(self, filename):
        self.zip = None
        self.dom = None
        self.contentfile = None
        self.filename = filename

    def load_epub(self):
        """Load an epub file."""
        self.zip = zipfile.ZipFile(self.filename)

    
