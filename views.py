import json
import os
import uuid

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_caption_path(upload_folder, filename):
    stem, _ = os.path.splitext(filename)
    return os.path.join(upload_folder, f'{stem}.caption.json')


def save_caption(upload_folder, filename, caption):
    caption_path = get_caption_path(upload_folder, filename)
    with open(caption_path, 'w', encoding='utf-8') as caption_file:
        json.dump({'caption': caption}, caption_file)


def read_caption(upload_folder, filename):
    caption_path = get_caption_path(upload_folder, filename)
    if not os.path.exists(caption_path):
        return ''

    try:
        with open(caption_path, 'r', encoding='utf-8') as caption_file:
            data = json.load(caption_file)
        return data.get('caption', '')
    except (json.JSONDecodeError, OSError):
        return ''


def delete_caption(upload_folder, filename):
    caption_path = get_caption_path(upload_folder, filename)
    if os.path.exists(caption_path):
        os.remove(caption_path)


views = Blueprint('views', __name__)


@views.route('/')
def home():
    uploads = []
    upload_folder = current_app.config['UPLOAD_FOLDER']
    for filename in sorted(os.listdir(upload_folder), reverse=True):
        if allowed_file(filename):
            uploads.append({
                'url': url_for('static', filename=f'uploads/{filename}'),
                'filename': filename,
                'caption': read_caption(upload_folder, filename),
            })
    return render_template("home.html", uploads=uploads)


@views.route('/upload-photo', methods=['GET', 'POST'])
def upload_photo():
    if session.get('user') != current_app.config['OWNER_EMAIL']:
        flash('Only the owner may upload photos.', 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('No file part in the form.', 'error')
            return redirect(url_for('views.upload_photo'))

        photo = request.files['photo']
        caption = request.form.get('caption', '').strip()
        if photo.filename == '':
            flash('Please choose a photo to upload.', 'error')
            return redirect(url_for('views.upload_photo'))

        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            name, ext = os.path.splitext(filename)
            saved_name = f"{name}_{uuid.uuid4().hex}{ext}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], saved_name)
            photo.save(save_path)
            save_caption(current_app.config['UPLOAD_FOLDER'], saved_name, caption)
            flash('Photo uploaded successfully.', 'success')
            return redirect(url_for('views.home'))

        flash('Only image files are allowed (png, jpg, jpeg, gif, webp).', 'error')
        return redirect(url_for('views.upload_photo'))

    return render_template('upload.html')


@views.route('/delete-photo/<filename>', methods=['POST'])
def delete_photo(filename):
    if session.get('user') != current_app.config['OWNER_EMAIL']:
        flash('Only the owner may delete photos.', 'error')
        return redirect(url_for('views.home'))

    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, filename)
    if os.path.exists(file_path) and allowed_file(filename):
        os.remove(file_path)
        delete_caption(upload_folder, filename)
        flash('Photo deleted successfully.', 'success')
    else:
        flash('Photo not found or invalid.', 'error')

    return redirect(url_for('views.home'))


@views.route('/update-caption/<filename>', methods=['POST'])
def update_caption(filename):
    if session.get('user') != current_app.config['OWNER_EMAIL']:
        flash('Only the owner may update notes.', 'error')
        return redirect(url_for('views.home'))

    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, filename)
    if not os.path.exists(file_path) or not allowed_file(filename):
        flash('Photo not found or invalid.', 'error')
        return redirect(url_for('views.home'))

    caption = request.form.get('caption', '').strip()
    save_caption(upload_folder, filename, caption)
    flash('Note saved successfully.', 'success')
    return redirect(url_for('views.home'))


@views.route('/contact')
def contact():
    return render_template("contact.html")

