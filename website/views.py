from collections import Counter
from pathlib import Path
from uuid import uuid4
import json
import os

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for
)

from flask_login import (
    current_user,
    login_required
)

from werkzeug.utils import secure_filename

from . import db
from .models import Note, Folder


views = Blueprint('views', __name__)


# ----------------------------
# ALLOWED FILE TYPES
# ----------------------------

ALLOWED_EXTENSIONS = {
    'pdf',
    'doc',
    'docx',
    'txt',
    'rtf',
    'md',
    'ppt',
    'pptx',
    'png',
    'jpg',
    'jpeg'
}


def allowed_file(filename):

    return (
        '.' in filename
        and
        filename.rsplit('.', 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ----------------------------
# HOME
# ----------------------------

@views.route('/')
@login_required
def home():

    all_items = sorted(
        current_user.notes,
        key=lambda n: (
            (not bool(n.pinned)),
            n.date
        ),
        reverse=True
    )

    notebook_counts = Counter(
        note.notebook or 'My Notes'
        for note in current_user.notes
    )

    pinned_count = sum(
        1 for note in current_user.notes
        if note.pinned
    )

    pdf_count = sum(
        1 for note in current_user.notes
        if note.file
    )

    stats = {
        'total_notes': len(current_user.notes),
        'notebooks': len(notebook_counts),
        'pinned_notes': pinned_count,
        'pdfs': pdf_count,
    }

    folders = Folder.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        'home.html',
        user=current_user,
        notes=all_items,
        stats=stats,
        folders=folders
    )


# ----------------------------
# ALL NOTES
# ----------------------------

@views.route('/all-notes')
@login_required
def all_notes():

    return render_template(
        "allnotes.html",
        user=current_user,
        notes=current_user.notes
    )


# ----------------------------
# NEW NOTE
# ----------------------------

@views.route('/new-note', methods=['GET', 'POST'])
@login_required
def new_note():

    folders = Folder.query.filter_by(
        user_id=current_user.id
    ).all()

    if request.method == 'POST':

        title = (
            request.form.get('title')
            or 'Untitled note'
        ).strip()

        data = (
            request.form.get('data')
            or ''
        ).strip()

        category = (
            request.form.get('category')
            or 'General'
        ).strip()

        folder_id = request.form.get('folder_id')

        if len(data) < 1:

            flash(
                'Note is too short!',
                category='error'
            )

        else:

            new_note = Note(
                title=title,
                data=data,
                category=category,
                user_id=current_user.id,
                folder_id=folder_id if folder_id else None
            )

            db.session.add(new_note)
            db.session.commit()

            flash(
                'New note created!',
                category='success'
            )

            return redirect(
                url_for('views.all_notes')
            )

    return render_template(
        "new_note.html",
        user=current_user,
        folders=folders
    )

    if request.method == 'POST':

        title = request.form.get('title')
        category = request.form.get('category')
        data = request.form.get('data')

        if len(title) < 1:
            flash('Title is too short.', category='error')

        else:

            new_note = Note(
                title=title,
                category=category,
                data=data,
                user_id=current_user.id
            )

            db.session.add(new_note)
            db.session.commit()

            flash('Note created!', category='success')

            return redirect(url_for('views.all_notes'))

    return render_template(
        'new_note.html',
        user=current_user
    )

    folders = Folder.query.filter_by(
        user_id=current_user.id
    ).all()

    if request.method == 'POST':

        title = (
            request.form.get('title')
            or 'Untitled note'
        ).strip()

        note_text = (
            request.form.get('note')
            or ''
        ).strip()

        category = (
            request.form.get('category')
            or 'General'
        ).strip()

        folder_id = request.form.get('folder_id')

        if len(note_text) < 1:

            flash(
                'Note is too short!',
                category='error'
            )

        else:

            new_note = Note(
                title=title,
                data=note_text,
                category=category,
                user_id=current_user.id,
                folder_id=folder_id if folder_id else None
            )

            db.session.add(new_note)
            db.session.commit()

            flash(
                'New note created!',
                category='success'
            )

            return redirect(
                url_for('views.home')
            )

    return render_template(
        "new_note.html",
        user=current_user,
        folders=folders
    )


# ----------------------------
# NEW FOLDER
# ----------------------------

@views.route('/new-folder', methods=['GET', 'POST'])
@login_required
def new_folder():

    if request.method == 'POST':

        folder_name = (
            request.form.get('folder_name')
            or ''
        ).strip()

        if folder_name:

            folder = Folder(
                name=folder_name,
                user_id=current_user.id
            )

            db.session.add(folder)
            db.session.commit()

            flash(
                'Folder created!',
                category='success'
            )

            return redirect(
                url_for('views.home')
            )

    return render_template(
        "new_folder.html",
        user=current_user
    )


# ----------------------------
# UPLOAD FILE
# ----------------------------

@views.route('/upload-pdf', methods=['GET', 'POST'])
@login_required
def upload_pdf():

    if request.method == 'GET':

        return render_template(
            "upload_pdf.html",
            user=current_user
        )

    title = (
        request.form.get('pdf_title')
        or ''
    ).strip()

    notebook = (
        request.form.get('pdf_notebook')
        or 'Reference Library'
    ).strip()

    tags = (
        request.form.get('pdf_tags')
        or ''
    ).strip()

    pinned = (
        request.form.get('pdf_pinned')
        == 'on'
    )

    uploaded_file = request.files.get('pdf_file')

    if not uploaded_file:

        flash(
            'Please choose a file.',
            category='error'
        )

        return redirect(
            url_for('views.upload_pdf')
        )

    if uploaded_file.filename == '':

        flash(
            'No file selected.',
            category='error'
        )

        return redirect(
            url_for('views.upload_pdf')
        )

    if not allowed_file(uploaded_file.filename):

        flash(
            'Unsupported file type.',
            category='error'
        )

        return redirect(
            url_for('views.upload_pdf')
        )

    safe_name = secure_filename(
        uploaded_file.filename
    )

    unique_name = (
        f"{uuid4().hex}_{safe_name}"
    )

    upload_folder = (
        current_app.config['UPLOAD_FOLDER']
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    save_path = (
        Path(upload_folder)
        / unique_name
    )

    uploaded_file.save(save_path)

    new_file = Note(
        title=title or Path(safe_name).stem,
        data='Uploaded study material',
        category='Upload',
        notebook=notebook,
        tags=tags,
        pinned=pinned,
        file=unique_name,
        user_id=current_user.id
    )

    db.session.add(new_file)
    db.session.commit()

    flash(
        'File uploaded successfully!',
        category='success'
    )

    return redirect(
        url_for('views.home')
    )


# ----------------------------
# VIEW UPLOADED FILE
# ----------------------------

@views.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):

    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        filename
    )


# ----------------------------
# DELETE NOTE
# ----------------------------

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():

    payload = json.loads(request.data)

    note_id = payload['noteId']

    note = Note.query.get(note_id)

    if note and note.user_id == current_user.id:

        if note.file:

            file_path = (
                Path(current_app.config['UPLOAD_FOLDER'])
                / note.file
            )

            if file_path.exists():
                file_path.unlink()

        db.session.delete(note)
        db.session.commit()

    return jsonify({})


# ----------------------------
# TOGGLE PIN
# ----------------------------

@views.route('/toggle-pin', methods=['POST'])
@login_required
def toggle_pin():

    payload = json.loads(request.data)

    note_id = payload['noteId']

    note = Note.query.get(note_id)

    if note and note.user_id == current_user.id:

        note.pinned = not bool(note.pinned)

        db.session.commit()

        return jsonify({
            'pinned': note.pinned
        })

    return jsonify({
        'error': 'Note not found'
    }), 404

@views.route('/note/<int:note_id>')
@login_required
def view_note(note_id):

    note = Note.query.get_or_404(note_id)

    if note.user_id != current_user.id:

        flash(
            "Unauthorized access.",
            category="error"
        )

        return redirect(
            url_for('views.home')
        )

    return render_template(
        "view_note.html",
        user=current_user,
        note=note
    )

@views.route('/folder/<int:folder_id>')
@login_required
def view_folder(folder_id):

    folder = Folder.query.get_or_404(folder_id)

    if folder.user_id != current_user.id:

        return redirect(
            url_for('views.home')
        )

    return render_template(
        "view_folder.html",
        user=current_user,
        folder=folder
    )