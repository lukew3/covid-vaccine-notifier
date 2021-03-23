from flask import Flask, Blueprint, flash, request, redirect, url_for, render_template, send_from_directory, jsonify, Response
import json

with open('config.json') as config_file:
    config = json.load(config_file)

app = Flask(__name__)
app.config['SECRET_KEY'] = config.get('SECRET_KEY')

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
