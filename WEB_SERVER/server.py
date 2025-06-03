from flask import jsonify, make_response
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_session import Session
from flask import Flask, session, url_for, request, jsonify, redirect 
from Algorithm import load_vehicle_data, process_unipol_data, process_google_maps_data, process_questionnaire_data, recommend_vehicles
from GoogleMaps_processing import process_zip
from Costs_calculation import *
import json
import os
import requests
from flask import send_file, Response
import io


file_path = ''




app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}},supports_credentials=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def hello():
    return 'Hello, Welcome to the server of BEST E-CAR application company'


