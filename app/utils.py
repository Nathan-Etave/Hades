from threading import Lock
from whoosh.fields import Schema, TEXT, STORED, KEYWORD, ID
from whoosh.index import create_in, open_dir
from whoosh.query import *
from whoosh.analysis import StandardAnalyzer
import os.path
from flask import current_app


class SingletonMeta(type):
    """Singleton metaclass.

    Args:
        type (type): Metaclass type.

    Returns:
        type: Metaclass type.
    """
    _instances = {}
    _lock = Lock()

    def __call__(self, *args, **kwargs):
        with self._lock:
            if self not in self._instances:
                instance = super().__call__(*args, **kwargs)
                self._instances[self] = instance
        return self._instances[self]
    

class whoosh(metaclass=SingletonMeta):
    def __init__(self):
        analyzer = StandardAnalyzer(stoplist=None)
        schema = Schema(title=TEXT(stored=True, analyzer=analyzer), content=TEXT(analyzer=analyzer), path=ID(stored=True), tags=KEYWORD(stored=True, commas=True, scorable=True, analyzer=analyzer), id=STORED)
        with current_app.app_context():
            if not os.path.exists(f'{current_app.root_path}/storage/index') :
                os.mkdir(f'{current_app.root_path}/storage/index')
                create_in(f'{current_app.root_path}/storage/index', schema)
            open_index = open_dir(f'{current_app.root_path}/storage/index')

        self.writer = open_index.writer()
        self.searcher = open_index.searcher()