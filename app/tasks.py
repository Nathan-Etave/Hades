import json
from datetime import datetime
from app import celery, create_app, redis, socketio
from celery import current_task
from app.utils import FileReader, NLPProcessor, Whoosh
from fasteners import InterProcessLock

@celery.task(name='app.tasks.process_file')
def process_file(file_path, filename, folder_id, file_id, user_tags, current_user, file, folder, action):
    app = create_app(is_worker=True)
    with app.app_context():
        worker_name = current_task.request.hostname
        redis.lpop('file_queue')
        if redis.llen('file_queue') > 0:
            next_file = redis.lindex('file_queue', 0).decode('utf-8')
        else:
            next_file = None
        redis.publish('worker_status', json.dumps({'worker': worker_name, 'status': 'processing', 'file': filename, 'next_file': next_file}))
        redis.set(f'worker:{worker_name}', json.dumps({'worker': worker_name, 'status': 'processing', 'file': filename, 'next_file': next_file}))
        file_text = FileReader().read(file_path, filename.split(".")[-1])
        file_tags = f'{' '.join(NLPProcessor().tokenize(file_text))} {user_tags}'
        with InterProcessLock(f'{app.root_path}/whoosh.lock'):
            Whoosh().add_document(filename, file_text, folder_id, file_tags, file_id)
        redis.rpush('processed_files', json.dumps({'filename': filename, 'folder_id': folder_id, 'file_id': file_id, 'user': current_user, 'file': file, 'folder': folder, 'action': action}))
        date_str = file['date_Fichier'].split(':')[0] + ':' + file['date_Fichier'].split(':')[1]
        file['date_Fichier'] = datetime.strptime(date_str, '%d/%m/%Y %H:%M').strftime('%d/%m/%Y %H:%M')
        redis.publish('file_processed', json.dumps({'filename': filename, 'folder_id': folder_id, 'file_id': file_id, 'user': current_user, 'file': file, 'folder': folder, 'action': action}))
        redis.publish('worker_status', json.dumps({'worker': worker_name, 'status': 'idle', 'file': None, 'next_file': None}))
        redis.incr('total_files_processed')
        redis.publish('process_status', json.dumps({'total_files': redis.get('total_files').decode('utf-8'), 'total_files_processed': redis.get('total_files_processed').decode('utf-8')}))
        redis.delete(f'worker:{worker_name}')