from flask import Flask, render_template, request, redirect
import os
import string
from models import User, History
from models import History
from database import db
from models import User
from flask import Flask, render_template, request, redirect, session
from backend.pdf_reader import extract_text
from backend.ocr import extract_text as ocr_text
from backend.web_scraper import extract_website_text
from backend.chatbot import ask_ai
from backend.sign_recognition import start_camera
app = Flask(__name__)

app.secret_key = "signbridge_secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    print("Creating database...")
    db.create_all()
    print("Database created successfully!")

import os
import string

@app.route("/translate", methods=["GET", "POST"])
def translate():

    output = []

    if request.method == "POST":

        text = request.form["text"].lower()

        text = text.translate(str.maketrans('', '', string.punctuation))

        words = text.split()

        sign_folder = os.path.join(app.static_folder, "signs")

        for word in words:

            word_image = word + ".png"

            if os.path.exists(os.path.join(sign_folder, word_image)):

                output.append({
                    "type": "word",
                    "images": [word_image],
                    "label": word.upper()
                })

            else:

                letters = []

                for letter in word.upper():

                    if os.path.exists(os.path.join(sign_folder, letter + ".png")):
                        letters.append(letter + ".png")

                output.append({
                    "type": "letters",
                    "images": letters,
                    "label": word.upper()
                })

    return render_template("translate.html", output=output)
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
@app.route("/")
def home():
    return render_template(
        "index.html",
        username=session.get("username")
    )

@app.route("/voice")
def voice():
    return render_template("voice.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        user = User(
            username=request.form["username"],
            password=request.form["password"]
        )

        db.session.add(user)
        db.session.commit()

        return "Registration Successful"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:
             session["username"] = user.username
             return redirect("/")

        return "Invalid Login"

    return render_template("login.html")
@app.route("/text")
def text():
    return render_template("text.html")

@app.route("/scan", methods=["GET", "POST"])
def scan():

    result = ""
    output = []

    if request.method == "POST":

        image = request.files["image"]

        if image:

            upload_path = os.path.join("static/uploads", image.filename)

            image.save(upload_path)

            result = ocr_text(upload_path)

            sign_folder = os.path.join(app.static_folder, "signs")

            import string

            text = result.lower()

            text = text.translate(str.maketrans('', '', string.punctuation))

            words = text.split()

            for word in words:

                word_img = word + ".png"

                if os.path.exists(os.path.join(sign_folder, word_img)):

                    output.append({
                        "type":"word",
                        "images":[word_img],
                        "label":word.upper()
                    })

                else:

                    letters=[]

                    for ch in word.upper():

                        img = ch + ".png"

                        if os.path.exists(os.path.join(sign_folder,img)):
                            letters.append(img)

                    output.append({
                        "type":"letters",
                        "images":letters,
                        "label":word.upper()
                    })

    return render_template(
        "scan.html",
        result=result,
        output=output
    )

@app.route("/pdf", methods=["GET","POST"])
def pdf():

    result=""
    output=[]

    if request.method=="POST":

        file=request.files["pdf"]

        if file:

            upload_path=os.path.join("static/uploads",file.filename)

            file.save(upload_path)

            result=extract_text(upload_path)
            print("PDF TEXT:")
            print(result)
            print("Extracted PDF Text:", result)

            sign_folder=os.path.join(app.static_folder,"signs")

            import string

            text=result.lower()

            text=text.translate(str.maketrans('','',string.punctuation))

            words=text.split()

            for word in words:

                word_img=word+".png"

                if os.path.exists(os.path.join(sign_folder,word_img)):

                    output.append({
                        "type":"word",
                        "images":[word_img],
                        "label":word.upper()
                    })

                else:

                    letters=[]

                    for ch in word.upper():

                        img=ch+".png"

                        if os.path.exists(os.path.join(sign_folder,img)):
                            letters.append(img)

                    output.append({
                        "type":"letters",
                        "images":letters,
                        "label":word.upper()
                    })

    return render_template(
        "pdf.html",
        result=result,
        output=output
    )

@app.route("/link", methods=["GET","POST"])
def link():

    result=""
    output=[]

    if request.method=="POST":

        url=request.form["url"]

        if url:

            result=extract_website_text(url)

            sign_folder=os.path.join(app.static_folder,"signs")

            import string

            text=result.lower()

            text=text.translate(str.maketrans('','',string.punctuation))

            words=text.split()

            for word in words:

                word_img=word+".png"

                if os.path.exists(os.path.join(sign_folder,word_img)):

                    output.append({
                        "type":"word",
                        "images":[word_img],
                        "label":word.upper()
                    })

                else:

                    letters=[]

                    for ch in word.upper():

                        img=ch+".png"

                        if os.path.exists(os.path.join(sign_folder,img)):
                            letters.append(img)

                    output.append({
                        "type":"letters",
                        "images":letters,
                        "label":word.upper()
                    })

    return render_template(
        "link.html",
        result=result,
        output=output
    )

@app.route("/chat", methods=["GET", "POST"])
def chat():

    answer = ""
    output = []

    if request.method == "POST":

        question = request.form["question"]

        try:
            answer = ask_ai(question)
        except Exception:
            answer = "⚠️ AI service is temporarily unavailable. Please try again later."

        sign_folder = os.path.join(app.static_folder, "signs")

        text = answer.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))

        words = text.split()

        for word in words:

            word_image = word + ".png"

            if os.path.exists(os.path.join(sign_folder, word_image)):

                output.append({
                    "type": "word",
                    "images": [word_image],
                    "label": word.upper()
                })

            else:

                letters = []

                for letter in word.upper():

                    img = letter + ".png"

                    if os.path.exists(os.path.join(sign_folder, img)):
                        letters.append(img)

                output.append({
                    "type": "letters",
                    "images": letters,
                    "label": word.upper()
                })

    return render_template(
        "chat.html",
        answer=answer,
        output=output
    )
@app.route("/dashboard")
def dashboard():

    total_users = User.query.count()

    total_history = History.query.count()

    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_history=total_history
    )
@app.route("/learn")
def learn():

    letters = []

    for i in range(65, 91):
        letters.append(chr(i))

    return render_template(
        "learn.html",
        letters=letters
    )
@app.route("/camera")
def camera():

    start_camera()

    return """
    <h2>Camera Closed Successfully</h2>

    <a href='/dashboard'>
        Back to Dashboard
    </a>
    """
@app.route("/history")
def history():

    records = History.query.order_by(History.id.desc()).all()

    return render_template(
        "history.html",
        records=records
    )
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)