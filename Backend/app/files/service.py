import os, re, mimetypes, time
from werkzeug.utils import secure_filename
from flask import url_for

STORAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))

# Extensiones permitidas por tipo (ajústalo a tus necesidades)
ALLOWED_EXT = {
    'images': {'.png', '.jpg', '.jpeg', '.gif', '.webp'},
    'docs':   {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'}
}

# Tamaño máximo (ej. 10 MB)
MAX_BYTES = 10 * 1024 * 1024

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def is_allowed(filename: str, modes=('images','docs')) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    allowed = set().union(*[ALLOWED_EXT[m] for m in modes if m in ALLOWED_EXT])
    return ext in allowed

def save_upload(file_storage, bucket: str, modes=('images','docs')):
   
    if not file_storage or not file_storage.filename:
        return None, "EMPTY_FILE"

    if not is_allowed(file_storage.filename, modes):
        return None, "INVALID_EXT"

    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)

    if size > MAX_BYTES:
        return None, "TOO_LARGE"

    ensure_dir(os.path.join(STORAGE_ROOT, bucket))
    base = secure_filename(file_storage.filename)
    ts = time.strftime('%Y%m%d%H%M%S')
    stored_name = f"{ts}_{base}"
    abs_path = os.path.join(STORAGE_ROOT, bucket, stored_name)
    file_storage.save(abs_path)

    mime, _ = mimetypes.guess_type(stored_name)
    return {
        "bucket": bucket,
        "stored_name": stored_name,
        "original_name": base,
        "size": size,
        "mime": mime or "application/octet-stream",
        "url": url_for('files.get_file', bucket=bucket, filename=stored_name, _external=False)
    }, None

def file_url(bucket: str, stored_name: str, external=False):
    if not stored_name:
        return None
    return url_for('files.get_file', bucket=bucket, filename=stored_name, _external=external)

def delete_file(bucket: str, stored_name: str):
    try:
        os.remove(os.path.join(STORAGE_ROOT, bucket, stored_name))
    except FileNotFoundError:
        pass
