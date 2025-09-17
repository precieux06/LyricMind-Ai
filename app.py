from flask import Flask, render_template, request, jsonify
import random

app = Flask(_name_)

Page principale
@app.route('/')
def index():
    return render_template('index.html')

API simple pour générer paroles (exemple)
@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    
    # Simuler une réponse (tu pourras brancher ton IA ici)
    lyrics = f"Paroles générées pour : {prompt}\n" + \
             "La musique dans mes veines, le rythme dans le sang..."
    
    return jsonify({'lyrics': lyrics})

if _name_ == '_main_':
    app.run(debug=True)
