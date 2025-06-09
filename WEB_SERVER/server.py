from flask import jsonify, make_response
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_session import Session
from flask import Flask, session, url_for, request, jsonify, redirect 
from Algorithm import load_vehicle_data, process_unipol_data, process_google_maps_data, process_questionnaire_data, recommend_vehicles
from GoogleMaps_processing import process_zip
from Costs_calculation import *
from flask import Flask, send_from_directory
import os
from flask import send_file, Response


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}},supports_credentials=True)

# Directory dove sono salvati i file CSV
DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'data')

@app.route('/')
def hello():
    return 'Hello, Welcome to the server of BEST E-CAR application company'


@app.route('/data/<path:filename>', methods=['GET'])
def serve_csv(filename):
    """Serve i file CSV richiesti dal frontend"""
    return send_from_directory(DATA_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)

