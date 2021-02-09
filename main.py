from flask_cors import CORS
from flask import Flask, render_template, request, redirect, url_for, Response, session
from datetime import datetime

from entities.user_entity import User
from entities.user_leisure_entity import UserLeisure

from dotenv import load_dotenv

import os
import json

app = Flask(__name__)

load_dotenv()
session_key = os.getenv('sessionPrivateKey')
app.secret_key = session_key

CORS(app)
mimetype = 'application/json'


@app.route('/', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':  # when an user enters with Google
        email = request.form['email']
        uid = request.form['uid']
        display_name = request.form['displayName']
        profile_picture = request.form['profilePicture']
        user = User.get_by_uid(uid)
        if user is None:
            User.create_user(uid, email, display_name, profile_picture)
        session['current_user_email'] = email
        session['current_user_uid'] = uid
        session['current_user_display_name'] = display_name
        session['current_user_profile_picture'] = profile_picture
        return json.dumps({'status': 'OK'})
    else:
        if 'current_user_uid' in session:
            return redirect(url_for('show_home'))
        else:
            return render_template('login.html', title='YATAM - Login')


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('current_user_email', None)
    session.pop('current_user_uid', None)
    session.pop('current_user_display_name', None)
    session.pop('current_user_profile_picture', None)

    return redirect(url_for('start'))


@app.route('/home', methods=['GET'])
def show_home():
    if 'current_user_uid' not in session:
        return redirect(url_for('start'))
    else:
        return render_template('home.html', title='Home')


@app.route('/map', methods=['GET', 'POST'])
def show_map():
    if 'current_user_uid' not in session:
        return redirect(url_for('start'))
    else:
        if request.method == 'POST':
            req = request.get_json()
            if req == "USERLEISURE":
                leisures = UserLeisure.search_by_user(session['current_user_uid'])
            return Response(response=json.dumps(leisures, default=lambda o: o.encode(), indent=4),
                            status=200,
                            mimetype=mimetype)
        else:
            return render_template('map.html', title='Map')


@app.route('/leisure/create', methods=['GET', 'POST'])
def create_leisure():
    leisure = None
    if 'current_user_uid' not in session:
        redirect(url_for('start'))
    else:
        if request.method == 'GET':
            return render_template('create_leisure.html', title='YATAM - Create User Leisure')
        elif request.method == 'POST':
            name = request.form['name']
            coordinates = request.form['coordinates']
            coordinates = coordinates.split(',')
            description = request.form['description']
            photo = request.form['photo']
            schedule = request.form['schedule']
            address = request.form['address']
            leisure = UserLeisure.create_user_leisure(name=name, coordinates=coordinates, description=description,
                                                      url_photo=photo,
                                                      schedule=schedule, address=address,
                                                      user=session['current_user_uid'])
        if leisure is not None:
            return Response(response=json.dumps({"key": leisure.key}), status=200, mimetype=mimetype)


if __name__ == '__main__':
    app.run()
