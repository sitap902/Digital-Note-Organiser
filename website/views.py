from collections import Counter
from pathlib import Path
from uuid import uuid4
import json

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from . import db
from .models import Note

views = Blueprint('views', __name__)
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        title = (request.form.get('title') or '').strip()
        note_text = (request.form.get('note') or '').strip()
        category = (request.form.get('category') or 'Lecture').strip()
        notebook = (request.form.get('notebook') or 'My Notes').strip()
        tags = (request.form.get('tags') or '').strip()
        pinned = request.form.get('pinned') == 'on'

        if len(note_text) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(
                title=title or 'Untitled note',
                data=note_text,
                category=category,
                notebook=notebook or 'My Notes',
                tags=tags,
                pinned=pinned,
                user_id=current_user.id,
            )
            db.session.add(new_note)
            db.session.commit()
            flash('Note saved to your organizer.', category='success')
            return redirect(url_for('views.home'))

    selected_notebook = (request.args.get('notebook') or 'All').strip()
    selected_type = (request.args.get('type') or 'All').strip()
    query = (request.args.get('q') or '').strip().lower()
    selected_id = request.args.get('selected')

    all_items = sorted(
        current_user.notes,
        key=lambda n: ((not bool(n.pinned)), n.date),
        reverse=True,
    )

    filtered_items = []
    for note in all_items:
        item_type = 'PDF' if note.file else 'Note'
        matches_notebook = selected_notebook == 'All' or note.notebook == selected_notebook
        matches_type = selected_type == 'All' or item_type == selected_type
        haystack = f"{note.title} {note.data} {note.tags} {note.notebook} {note.category} {Path(note.file).name if note.file else ''}".lower()
        matches_query = not query or query in haystack

        if matches_notebook and matches_type and matches_query:
            filtered_items.append(note)

    notebook_counts = Counter(note.notebook or 'My Notes' for note in current_user.notes)
    type_counts = Counter('PDF' if note.file else 'Note' for note in current_user.notes)
    pinned_count = sum(1 for note in current_user.notes if note.pinned)
    pdf_count = sum(1 for note in current_user.notes if note.file)

    active_item = None
    if selected_id:
        active_item = next((item for item in filtered_items if str(item.id) == str(selected_id)), None)
    if active_item is None and filtered_items:
        active_item = filtered_items[0]

    stats = {
        'total_notes': len(current_user.notes),
        'filtered_notes': len(filtered_items),
        'notebooks': len(notebook_counts),
        'pinned_notes': pinned_count,
        'pdfs': pdf_count,
    }

    return render_template(
        'home.html',
        user=current_user,
        notes=filtered_items,
        active_note=active_item,
        notebook_counts=dict(sorted(notebook_counts.items())),
        type_counts=dict(sorted(type_counts.items())),
        selected_notebook=selected_notebook,
        selected_type=selected_type,
        query=query,
        stats=stats,
    )


@views.route('/upload-pdf', methods=['POST'])
@login_required
def upload_pdf():
    title = (request.form.get('pdf_title') or '').strip()
    notebook = (request.form.get('pdf_notebook') or 'Reference Library').strip()
    tags = (request.form.get('pdf_tags') or '').strip()
    pinned = request.form.get('pdf_pinned') == 'on'
    uploaded_file = request.files.get('pdf_file')

    if not uploaded_file or uploaded_file.filename == '':
        flash('Choose a PDF to upload.', category='error')
        return redirect(url_for('views.home'))

    if not allowed_file(uploaded_file.filename):
        flash('Only PDF files are supported.', category='error')
        return redirect(url_for('views.home'))

    safe_name = secure_filename(uploaded_file.filename)
    unique_name = f"{uuid4().hex}_{safe_name}"
    save_path = Path(current_app.config['UPLOAD_FOLDER']) / unique_name
    uploaded_file.save(save_path)

    new_pdf = Note(
        title=title or Path(safe_name).stem,
        data='Uploaded PDF resource',
        category='PDF',
        notebook=notebook or 'Reference Library',
        tags=tags,
        pinned=pinned,
        file=unique_name,
        user_id=current_user.id,
    )
    db.session.add(new_pdf)
    db.session.commit()
    flash('PDF uploaded to your organizer.', category='success')
    return redirect(url_for('views.home', selected=new_pdf.id))


@views.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    payload = json.loads(request.data)
    note_id = payload['noteId']
    note = Note.query.get(note_id)
    if note and note.user_id == current_user.id:
        if note.file:
            file_path = Path(current_app.config['UPLOAD_FOLDER']) / note.file
            if file_path.exists():
                file_path.unlink()
        db.session.delete(note)
        db.session.commit()

    return jsonify({})


@views.route('/toggle-pin', methods=['POST'])
@login_required
def toggle_pin():
    payload = json.loads(request.data)
    note_id = payload['noteId']
    note = Note.query.get(note_id)
    if note and note.user_id == current_user.id:
        note.pinned = not bool(note.pinned)
        db.session.commit()
        return jsonify({'pinned': note.pinned})

    return jsonify({'error': 'Note not found'}), 404
