from email import message
import os
import pyrebase
from flask import Flask, render_template, request, send_file, redirect, url_for, session, flash
import firebase_admin
from firebase_admin import credentials, storage, db
import datetime
import tempfile

app = Flask(__name__)
config = {
    "apiKey": "AIzaSyCqokofnUII64JCU2XBWwETDmv3ULFFFGE",
    "authDomain": "nyaysetu-c6500.firebaseapp.com",
    "databaseURL": "https://nyaysetu-c6500-default-rtdb.firebaseio.com",
    "projectId": "nyaysetu-c6500",
    "storageBucket": "nyaysetu-c6500.appspot.com",
    "messagingSenderId": "351368719023",
    "appId": "1:351368719023:web:d2a5f389def9347dfb025a",
    "measurementId": "G-XC05M13SYK"
}

cred = credentials.Certificate("nyaysetu-c6500-firebase-adminsdk-jr9vt-288feca55d.json")
firebase = firebase_admin.initialize_app(cred, {
    'databaseURL': config['databaseURL'],
    'storageBucket': config['storageBucket']
})

firebase1 = pyrebase.initialize_app(config)
auth = firebase1.auth()
bucket = storage.bucket()

app.config["SECRET_KEY"] = "thidifh"

@app.before_request
def check_authentication():
    allowed_endpoints = ['ho', 'login', 'signup', 'createaccount']
    if request.endpoint not in allowed_endpoints and 'user_id' not in session:
        return redirect(url_for('login'))

@app.route('/')
def ho():
    return render_template("index.html")

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        try:
            email = request.form.get("email")
            password = request.form.get("password")
            user = auth.create_user_with_email_and_password(email, password)
            session['user_id'] = user['localId']
            session['id_token'] = user['idToken']
            session['email'] = email
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash("Error creating account. Please try again.")
            return render_template("create.html")
    return render_template("create.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user_id'] = user['localId']
            session['id_token'] = user['idToken']
            session['email'] = email
            return redirect(url_for('dashboard'))
        except:
            flash("Invalid credentials. Please try again.")
            return render_template("create.html")
    return render_template("create.html")

@app.route("/create")
def createaccount():
    return render_template('create.html')
from datetime import datetime, timedelta, timezone

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    uid = session['user_id']
    user_email = session['email']
    files = []
    
    user_files_ref = db.reference(f'users/{uid}/files').get()
    now = datetime.now(timezone.utc)

    if user_files_ref:
        for file_id, file_data in user_files_ref.items():
            blob = bucket.blob(file_data['path'])
            
            # Get timestamps in UTC
            uploaded_at = datetime.fromtimestamp(file_data['uploaded_at'] / 1000, tz=timezone.utc)
            expiry_minutes = file_data.get('expiry_minutes', 5)
            expiration_time = uploaded_at + timedelta(minutes=expiry_minutes)
            
            # Check if file should be deleted
            if now > expiration_time + timedelta(minutes=5):  # Grace period
                # Delete expired file
                blob.delete()
                db.reference(f'users/{uid}/files/{file_id}').delete()
                continue
                
            # Calculate remaining time
            remaining = expiration_time - now
            expires_in = max(0, int(remaining.total_seconds() // 60))
            is_expired = remaining.total_seconds() <= 0

            # Generate URL only if not expired
            signed_url = None
            if not is_expired:
                signed_url = blob.generate_signed_url(
                    expiration=expiration_time,
                    method='GET',
                    response_disposition=f'attachment; filename="{file_data["name"]}"'
                )

            files.append({
                'name': file_data['name'],
                'url': signed_url,
                'expires_in': expires_in,
                'expired': is_expired
            })

    return render_template('dashboard.html', 
                         files=files,
                         user_email=user_email)

@app.route('/uploader', methods=['POST'])
def uploader():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    uid = session['user_id']
    expiry_minutes = int(request.form.get('expiry_time', 5))
    
    # Validate maximum expiry time (7 days)
    if expiry_minutes > 10080:
        expiry_minutes = 10080
        flash("Maximum expiry time is 7 days")

    if request.method == 'POST':
        f = request.files['fileinput']
        display_name = request.form.get('nameinput', f.filename)
        
        if f:
            blob_path = f"users/{uid}/files/{f.filename}"
            blob = bucket.blob(blob_path)
            blob.upload_from_file(f, content_type=f.content_type)
            
            file_data = {
                'name': display_name,
                'path': blob_path,
                'uploaded_at': {'.sv': 'timestamp'},
                'expiry_minutes': expiry_minutes
            }
            db.reference(f'users/{uid}/files').push(file_data)
            flash('File uploaded successfully!')
        
        return redirect(url_for('dashboard'))
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for('ho'))

if __name__ == "__main__":
    app.run(debug=True)