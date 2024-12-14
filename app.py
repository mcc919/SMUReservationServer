from flask import Flask, request, jsonify
from sangmyung_univ_auth import auth

app = Flask(__name__)

@app.route('/')
def index():
    return '<p>hello world</p>'

@app.route('/login', methods=['POST'])
def login():
    result = auth(request.form['username'], request.form['password'])
    result = result._asdict()   # AuthResponse를 dictionary 형태로 변환
    
    return jsonify(result)