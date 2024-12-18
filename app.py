from dotenv import load_dotenv
import os 

from flask import Flask, request, jsonify
from sangmyung_univ_auth import auth

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

# load .env
load_dotenv()
JWT_KEY = os.environ.get('JWT_KEY')

# create App
app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = JWT_KEY
jwt = JWTManager(app)

@app.route('/')
def index():
    return '<p>hello world</p>'

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    result = auth(username, password)
    result = result._asdict()   # AuthResponse를 dictionary 형태로 변환

    access_token = create_access_token(identity=username)

    if result["is_auth"]:
        result['access_token'] = access_token
    
    
    return jsonify(result)


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/validateToken", methods=["GET"])
@jwt_required()
def validateToken():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)