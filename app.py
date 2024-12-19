
from email import message
import os
import pyrebase
from flask import Flask, render_template, request, send_file
from flask import flash
import firebase_admin
from firebase_admin import credentials
from firebase_admin import credentials, firestore, storage,db
import tempfile


app = Flask(__name__)
config={
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
path_on_cloud="files/"

firebase = firebase_admin.initialize_app(cred,{
    'databaseURL':'https://nyaysetu-c6500-default-rtdb.firebaseio.com/',
    "storageBucket": "nyaysetu-c6500.appspot.com"

})
firebase1= pyrebase.initialize_app(config)

bucket = storage.bucket()
auth=firebase1.auth()

app.config["SECRET_KEY"] ="thidifh"
# storage=fire

@app.route('/')
def ho():
    return render_template("/index.html")


@app.route("/signup", methods=['post', 'get'])
def signup():
    print("message", request.form)
    
    message = 'Signup to your account'

    if request.method == "POST":
        try:
            name = request.form.get("name")

            email = request.form.get("email")
            password1 = request.form.get("password")

            user=auth.create_user_with_email_and_password(email,password1)
            auth.get_account_info(user['idToken'])
            return render_template("/dashboard.html")
        
        except Exception as e:
            e="Check your email address"
            flash(e)
            return render_template("/create.html")
        


@app.route("/login", methods=["POST", "GET"])
def login():
    messages ='Please check your username and password'

    if request.method == "POST":
        try:
            email = request.form.get("email")
            password = request.form.get("password")
            
            user=auth.sign_in_with_email_and_password(email, password)
            auth.get_account_info(user['idToken'])

            return render_template("/dashboard.html", message=messages)
        except Exception as e:
            e='Please check your username and password'
            flash(e)
            return render_template("/create.html", message=messages )
        


@app.route("/create")
def createaccount():
    return render_template('create.html')

@app.route("/sendfile")
def send():
    url = request.args.get("url")

    filename=os.path.basename(url)
    import requests
    r = requests.get(url, allow_redirects=True)
    
    ex = r.headers.get('content-type').split('/')[-1]
    open(f'{filename}.{ex}', 'wb').write(r.content)
    flash("successfully Downloaded",'success')
    return send_file(f'{filename}.{ex}', as_attachment=True)





@app.route('/uploader', methods=['POST', 'GET'])
def uploader():
    if request.method == 'POST':
        f = request.files['fileinput']
        message="Successfully Uploaded"
        global name
        name=request.form.get('nameinput')
        
        typee=f.content_type
        print(typee)
        temp = tempfile.NamedTemporaryFile(delete=False)
        f.save(temp.name)
        with open(temp.name, 'rb') as file:
            content = file.read()
            # print(content)
            
            name=f.filename
            # file_data = requests.get(content).content
            blob = bucket.blob(name)
            blob.upload_from_string(
               content,
               content_type=typee)
            blob.make_public()
            print(blob.public_url)
            
            # aler="Successfully Uploaded"
            # message=str(aler)
            
            
            users_data={'name':name, 'public_url':blob.public_url}
            db.reference('users').push(users_data)
            flash(message)
        return render_template("index.html")

@app.route('/search', methods=['POST'])
def download():
    info = db.reference('users').get()
    b = []
    for key, value in info.items():
        b.append(value)
        print(value)
    return render_template("downloads.html", a=b)


@app.route("/logout", methods=['POST', 'GET'])
def logout():
    auth.current_user=None
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
