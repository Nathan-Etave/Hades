from threading import Lock
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
