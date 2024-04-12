from threading import Lock
from whoosh.fields import Schema, TEXT, STORED, KEYWORD, ID
from whoosh.index import create_in, open_dir
from whoosh.query import *
from whoosh.analysis import StandardAnalyzer
import os.path
from flask import current_app
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop
from spacy.lang.en.stop_words import STOP_WORDS as en_stop
from spacy.util import compile_infix_regex
from spacy import load
from unidecode import unidecode

class SingletonMeta(type):
    """Singleton metaclass.

    Args:
        type (type): Metaclass type.

    Returns:
        type: Metaclass type.
    """
    _instances = {}
    _lock = Lock()
    
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
    

class Whoosh(metaclass=SingletonMeta):
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

    def add_document(self, title, content, path, tags, id):
        self.writer.add_document(title=title, content=content, path=path, tags=tags, id=id)
        self.writer.commit()

    def search(self, query, path):
        or_conditions = query.split("|")
        conditions = [condition.split('&') for condition in or_conditions]
        subquery = And([Term("path", path.strip().replace(" ", "")), Or([And([Or([Term("content", condition.strip().replace(" ", "")), Term("tags", condition.strip().replace(" ", ""))]) for condition in condition_list]) for condition_list in conditions])])
        return self.searcher.search(subquery)
    

class NLPProcessor(metaclass=SingletonMeta):
    def __init__(self, batch_size=100000):
        self.batch_size = batch_size
        self.tokenizer_nlp = load("model")
        self.lemmatizer_nlp = load("fr_dep_news_trf")
        self.tokenizer_nlp.max_length = batch_size
        self.lemmatizer_nlp.max_length = batch_size
        default_infixes = list(self.tokenizer_nlp.Defaults.infixes)
        default_infixes.append("[A-Z][a-z0-9]+")
        infix_regex = compile_infix_regex(default_infixes)
        self.tokenizer_nlp.tokenizer.infix_finditer = infix_regex.finditer
        self.stop_words = fr_stop.union(en_stop)

    def clean(self, text):
        return [
            unidecode(token.text)
            for token in self.tokenizer_nlp(text)
            if not unidecode(token.text) in self.stop_words
            and len(token) >= 3
            and not token.is_stop
            and not token.is_punct
            and not token.is_space
            and not token.like_url
            and not token.like_email
            and not token.is_digit
            and not token.is_currency
        ]

    def lemmatize(self, text):
        batches = [
            text[i : i + self.batch_size] for i in range(0, len(text), self.batch_size)
        ]
        text = ""
        with ThreadPoolExecutor() as executor:
            for batch in executor.map(self.process_lemmatize_batch, batches):
                text += " ".join(token.lemma_ for token in batch)
        return text

    def process_lemmatize_batch(self, batch):
        return self.lemmatizer_nlp(batch)

    def tokenize(self, text):
        text = self.lemmatize(text)
        batches = [
            text[i : i + self.batch_size] for i in range(0, len(text), self.batch_size)
        ]
        word_frequencies = {}
        with ThreadPoolExecutor() as executor:
            for batch in executor.map(self.process_tokenize_batch, batches):
                word_frequencies.update(batch)
        word_frequencies = sorted(
            word_frequencies.items(), key=lambda x: x[1], reverse=True
        )
        return [word for word, _ in word_frequencies]

    def process_tokenize_batch(self, batch):
        return Counter(self.clean(batch))
