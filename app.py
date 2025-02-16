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

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    uid = session['user_id']
    # Get user info from Firebase

    
    files = []
    user_files_ref = db.reference(f'users/{uid}/files').get()
    user_email = session['email']

    if user_files_ref:
        for file_id, file_data in user_files_ref.items():
            blob = bucket.blob(file_data['path'])
            signed_url = blob.generate_signed_url(
                expiration=datetime.timedelta(minutes=5),
                method='GET',
                response_disposition=f'attachment; filename="{file_data["name"]}"'
            )
            
            files.append({
                'name': file_data['name'],
                'url': signed_url,
                'expires_in': 5
            })

    return render_template('dashboard.html', files=files, user_email=user_email)

@app.route('/uploader', methods=['POST'])
def uploader():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    uid = session['user_id']
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
                'uploaded_at': {'.sv': 'timestamp'}
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
