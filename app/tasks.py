import time
from app import celery, create_app
from app.utils import FileReader, NLPProcessor, Whoosh
from whoosh.index import LockError
from fasteners import InterProcessLock

@celery.task(name='app.tasks.process_file')
def process_file(file_path, filename, folder_id, file_id):
    app = create_app()
    with app.app_context():
        file_text = FileReader().read(file_path, filename.split(".")[-1])
        file_tags = ' '.join(NLPProcessor().tokenize(file_text))
        with InterProcessLock(f'{app.root_path}/whoosh.lock'):
            Whoosh().add_document(filename, file_text, folder_id, file_tags, file_id)