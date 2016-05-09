from flask import Blueprint, render_template, request, g, redirect, url_for, session, abort, flash, jsonify, json, Response
from functools import wraps
import psycopg2
import psycopg2.extras
from flask_bootstrap import Bootstrap
import forms
import config
import models
from datetime import datetime
import statistics

from ressources import *

users_api = Blueprint('users_api', __name__)

@users_api.route("/login", methods=['GET', 'POST'])
def login():
    form = forms.Login(request.form)
    if request.method == "POST" and form.validate():
        query = "SELECT * FROM users WHERE username=%s"
        g.cursor.execute(query, [form.username.data])
        row = g.cursor.fetchone()
        if row:
            user = models.User.from_dict(row)
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            form.username.errors.append("Nom d'utilisateur ou mot de passe invalide")
            form.password.errors.append("Nom d'utilisateur ou mot de passe invalide")

    return render_template('login.html', form=form)

@users_api.route("/<int:pk>")
def profile(pk):
    query = "SELECT * FROM users WHERE id=%s"
    user = models.get_or_404(query, [pk], models.User)
    return render_template('profile.html', profile=user)

@users_api.route("/logout")
def logout():
    if "user_id" in session:
        del session['user_id']
    return redirect(url_for('index'))
