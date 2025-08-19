from flask import Blueprint, send_from_directory, abort, current_app
import os

files_bp = Blueprint('files', __name__, url_prefix='/files')

def storage_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))

@files_bp.route('/<bucket>/<path:filename>')
def get_file(bucket, filename):
    root = storage_root()
    folder = os.path.join(root, bucket)
    if not os.path.isdir(folder):
        abort(404)
    return send_from_directory(folder, filename)  # maneja 404 si no existe
