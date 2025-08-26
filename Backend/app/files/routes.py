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
    return send_from_directory(folder, filename) 

@files_bp.route('/download/<bucket>/<path:filename>')
def download_file(bucket, filename):
    root = storage_root()
    folder = os.path.join(root, bucket)
    if not os.path.isdir(folder):
        abort(404)
    return send_from_directory(folder, filename, as_attachment=True)