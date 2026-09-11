import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from dotenv import load_dotenv
from app.models import db, Note

# Load environment variables from .env if present
load_dotenv()


def create_app(test_config=None):
    """
    Application factory pattern for Flask.
    Allows easy instantiation for development, testing, and production.
    """
    app = Flask(__name__, template_folder='templates')

    # Default configuration
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///notes.db')
    # Fix SQLAlchemy compatibility for 'postgres://' URLs (e.g. from older cloud providers)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Apply test overrides if passed
    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)

    # Create tables automatically within app context
    with app.app_context():
        db.create_all()

    # --- Health Check Endpoint (Used for CI/CD Smoke Testing) ---
    @app.route('/health')
    def health_check():
        """
        Health check endpoint for smoke tests and container orchestration.
        Verifies both web app responsiveness and database connectivity.
        """
        try:
            # Perform a quick database ping
            db.session.execute(db.text('SELECT 1'))
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'environment': os.environ.get('FLASK_ENV', 'development')
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500

    # --- Routes for CRUD Operations ---

    # 1. READ ALL: Home page listing all notes
    @app.route('/')
    def index():
        notes = Note.query.order_by(Note.updated_at.desc()).all()
        return render_template('index.html', notes=notes)

    # 2. CREATE: Form & submission handler for creating a note
    @app.route('/notes/new', methods=['GET', 'POST'])
    def create_note():
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()

            if not title:
                flash('Title is required!', 'error')
                return render_template('create.html')

            note = Note(title=title, content=content)
            db.session.add(note)
            db.session.commit()
            flash('Note created successfully!', 'success')
            return redirect(url_for('view_note', note_id=note.id))

        return render_template('create.html')

    # 3. READ ONE: View a single rendered note
    @app.route('/notes/<int:note_id>')
    def view_note(note_id):
        note = db.get_or_404(Note, note_id)
        return render_template('view.html', note=note)

    # 4. UPDATE: Form & submission handler for editing a note
    @app.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
    def edit_note(note_id):
        note = db.get_or_404(Note, note_id)

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()

            if not title:
                flash('Title cannot be empty!', 'error')
                return render_template('edit.html', note=note)

            note.title = title
            note.content = content
            db.session.commit()
            flash('Note updated successfully!', 'success')
            return redirect(url_for('view_note', note_id=note.id))

        return render_template('edit.html', note=note)

    # 5. DELETE: Remove a note
    @app.route('/notes/<int:note_id>/delete', methods=['POST'])
    def delete_note(note_id):
        note = db.get_or_404(Note, note_id)
        db.session.delete(note)
        db.session.commit()
        flash('Note deleted successfully!', 'success')
        return redirect(url_for('index'))

    # JSON API Endpoint (Useful for testing & automation)
    @app.route('/api/notes', methods=['GET'])
    def api_get_notes():
        notes = Note.query.order_by(Note.updated_at.desc()).all()
        return jsonify([note.to_dict() for note in notes]), 200

    return app


# Application entrypoint when running directly
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
