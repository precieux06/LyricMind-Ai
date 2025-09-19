from flask import Flask, request, redirect, url_for, session, render_template, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from openai import OpenAI

# Charger variables d'environnement
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "Lyricmind_dev_key")

DB_NAME = "users.db"

# Initialisation API OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --- DB INIT ---
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )"""
        )
        conn.commit()


init_db()


# --- ROUTES ---
@app.route("/")
def index():
    if "user_id" in session:
        return render_template("index.html", nom=session.get("user_nom"))
    return redirect(url_for("login"))


# --- INSCRIPTION ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom = request.form["nom"]
        email = request.form["email"]
        password = request.form["password"]
        hashed = generate_password_hash(password)

        try:
            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT INTO users (nom, email, password) VALUES (?, ?, ?)",
                    (nom, email, hashed),
                )
                conn.commit()
            flash("Inscription réussie, connectez-vous !", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Cet email est déjà utilisé.", "error")

    return render_template("register.html")


# --- CONNEXION ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT id, nom, password FROM users WHERE email = ?", (email,))
            user = c.fetchone()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["user_nom"] = user[1]
            return redirect(url_for("index"))
        else:
            flash("Email ou mot de passe incorrect.", "error")

    return render_template("login.html")


# --- DECONNEXION ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# --- PAGE STUDIO (Génération IA) ---
@app.route("/studio", methods=["GET", "POST"])
def studio():
    if "user_id" not in session:
        return redirect(url_for("login"))

    result = None
    if request.method == "POST":
        prompt = request.form["prompt"]

        # Appel API OpenAI pour générer un clip/texte créatif
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un assistant créatif pour écrire des clips musicaux."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
        )

        result = response.choices[0].message.content

    return render_template("studio.html", result=result)


# --- MAIN ---
if __name__ == "__main__":
    app.run(debug=True)
