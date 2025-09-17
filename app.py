from flask import Flask, request, redirect, url_for, session, render_template_string, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(_name_)
app.secret_key = 'ta_cle_secrete_pour_session'  # Change ça !

DB_NAME = 'users.db'

Création table users si n'existe pas
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        conn.commit()

init_db()

Page d'accueil simple, montre si connecté ou pas
@app.route('/')
def index():
    if 'user_id' in session:
        return render_template_string("""
            <h1>Bienvenue {{ nom }} !</h1>
            <p><a href="{{ url_for('logout') }}">Déconnexion</a></p>
        """, nom=session.get('user_nom'))
return redirect(url_for('login'))

Inscription
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        password = request.form['password']
        hashed = generate_password_hash(password)

        try:
            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (nom, email, password) VALUES (?, ?, ?)", (nom, email, hashed))
                conn.commit()
            flash("Inscription réussie, connectez-vous !", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Cet email est déjà utilisé.", "error")

    return render_template_string("""
        <h2>Inscription</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% for category, message in messages %}
            <p style="color: {% if category=='error' %}red{% else %}green{% endif %};">{{ message }}</p>
          {% endfor %}
        {% endwith %}
        <form method="post">
            Nom: <input type="text" name="nom" required><br>
            Email: <input type="email" name="email" required><br>
Mot de passe: <input type="password" name="password" required><br>
            <button type="submit">S'inscrire</button>
        </form>
        <p>Déjà inscrit ? <a href="{{ url_for('login') }}">Connectez-vous ici</a></p>
    """)

Connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT id, nom, password FROM users WHERE email = ?", (email,))
            user = c.fetchone()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['user_nom'] = user[1]
            return redirect(url_for('index'))
        else:
            flash("Email ou mot de passe incorrect.", "error")

    return render_template_string("""
        <h2>Connexion</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% for category, message in messages %}
            <p style="color: red;">{{ message }}</p>
          {% endfor %}
        {% endwith %}
        <form method="post">
            Email: <input type="email" name="email" required><br>
Mot de passe: <input type="password" name="password" required><br>
            <button type="submit">Se connecter</button>
        </form>
        <p>Pas encore inscrit ? <a href="{{ url_for('register') }}">Inscrivez-vous ici</a></p>
    """)

Déconnexion
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if _name_ == '_main_':
    # debug=True en local seulement !
    app.run(debug=True)
