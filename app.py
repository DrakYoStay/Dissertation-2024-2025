from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
import face_recognition
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import json
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from devTools.database import Base, User
from devTools.blinkutils import detect_liveness_from_frames

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Load secret key for encryption
load_dotenv()
SECRET_KEY = os.getenv("FERNET_KEY").encode()
cipher = Fernet(SECRET_KEY)

# Setup SQLite
engine = create_engine('sqlite:///users.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

@app.route('/')
def index():
    user = session.get('user')
    current_user = db_session.query(User).filter_by(username=user).first() if user else None
    return render_template("index.html", user=user, user_type=current_user.user_type if current_user else None)

@app.route('/login-page')
def login_page():
    return render_template("login.html")

@app.route('/register-page')
def register_page():
    return render_template("register.html")

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    name = data['name']

    if db_session.query(User).filter_by(username=name).first():
        return jsonify({"message": f"Username '{name}' already exists."}), 409

    frames = data.get('frames')

    if not frames or not detect_liveness_from_frames(frames):
        return jsonify({"message": "Blink and motion not detected — please blink and move a bit during capture."}), 403

    face_encodings = face_recognition.face_encodings(img_np)
    if not face_encodings:
        return jsonify({"message": "No face detected."}), 400

    user = User(username=name, user_type='default_user')
    user.set_encoding(face_encodings[0])
    db_session.add(user)
    db_session.commit()

    return jsonify({"message": f"User '{name}' registered successfully!"})

@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    name = data.get('name')

    user = db_session.query(User).filter_by(username=name).first()
    if not user:
        return jsonify({"message": "Username not found."}), 404

    frames = data.get('frames')

    if not frames or not detect_liveness_from_frames(frames):
        return jsonify({"message": "Blink and motion not detected — please blink and move a bit during capture."}), 403

    for frame in frames:
        face_encodings = face_recognition.face_encodings(frame)
        if not face_encodings:
            return jsonify({"message": "No face detected."}), 400
        else:
            return jsonify({"message": "Log in successfully"})

    input_encoding = face_encodings[0]
    match = face_recognition.compare_faces([user.get_encoding()], input_encoding)[0]

    if match:
        session['user'] = name
        return jsonify({"message": f"Welcome, {name}!"})
    else:
        return jsonify({"message": "Face does not match username. Please try again."}), 401

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = db_session.query(User).filter_by(id=user_id).first()
    if user:
        db_session.delete(user)
        db_session.commit()
        return redirect(url_for('admin_dashboard'))
    return "User not found", 404

@app.route('/admin')
def admin_dashboard():
    current_user = db_session.query(User).filter_by(username=session.get('user')).first()
    if not current_user or current_user.user_type != 'admin':
        return "Access denied", 403

    users = db_session.query(User).all()
    return render_template("admin.html", users=users)

@app.route('/update-role/<int:user_id>', methods=['POST'])
def update_user_role(user_id):
    current_username = session.get('user')
    current_user = db_session.query(User).filter_by(username=current_username).first()

    # Don't allow regular users to access
    if not current_user or current_user.user_type != 'admin':
        return "Access denied", 403

    # Optional: prevent demoting yourself
    if current_user.id == user_id:
        return "You cannot change your own privileges.", 403

    new_role = request.form.get('user_type')
    user = db_session.query(User).filter_by(id=user_id).first()

    if user:
        user.user_type = new_role
        db_session.commit()
        flash(f"{user.username} is now a {new_role}.")
        return redirect(url_for('admin_dashboard'))
    return "User not found", 404



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
