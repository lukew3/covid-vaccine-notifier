from flask import Flask, Blueprint, flash, request, redirect, url_for, render_template, send_from_directory, jsonify, Response
from pymongo import MongoClient
import requests, time, json, threading
import re

with open('config.json') as config_file:
    config = json.load(config_file)

app = Flask(__name__)
app.config['SECRET_KEY'] = config.get('SECRET_KEY')
client = MongoClient('localhost', 27017)
users = client.vaccineNotifier.users

def zip_parser(zip_code):
    r = requests.get(f'https://public.opendatasoft.com/api/records/1.0/search/?dataset=us-zip-code-latitude-and-longitude&q={zip_code}&facet=state&facet=timezone&facet=dst')
    zip_dict = r.json()
    coords = zip_dict["records"][0]["geometry"]["coordinates"]
    state = zip_dict["records"][0]["fields"]["state"]
    return coords, state


def check_input(email, zipcode):
    email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if not (re.search(email_regex,email)):
        return "Invalid email"
    zipcode_regex = '^\d{5}(?:[-\s]\d{4})?$'
    if not (re.search(zipcode_regex, zipcode)):
        return "Invalid zip code"
    if users.find_one({"email": email}):
        return "Duplicate email"
    return "good"

@app.route('/', methods=['GET', 'POST'])
def home():
    message=''
    if request.method == 'POST':
        email = request.form.get('email')  # access the data inside
        zipcode = request.form.get('zipcode')
        distance = int(request.form.get('distance'))
        if check_input(email, zipcode) != "good":
            return render_template("home.html", message=check_input(email, zipcode))
        coords, state = zip_parser(zipcode)
        new_user = {"email": email,
                    "zipcode": zipcode,
                    "distance": distance,
                    "coords": coords,
                    "state": state,
                    "active": True }
        user_id = users.insert_one(new_user).inserted_id
        message='Registration success'
    return render_template("home.html", message=message)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
