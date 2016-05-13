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
from pbkdf2 import crypt

from ressources import *

users_api = Blueprint('users_api', __name__)

@users_api.route("/login", methods=['GET', 'POST'])
def login():
    form = forms.Login(request.form)
    if request.method == "POST" and form.validate():
        query = "SELECT * FROM users WHERE lower(username)=lower(%s)"
        username = form.username.data
        password =  form.password.data

        g.cursor.execute(query, [username])
        row = g.cursor.fetchone()
        if row:
            user = models.User.from_dict(row)
            if crypt(password, "s3c3tS4lT") != user.password:
                form.password.errors.append("Mot de passe invalide")
            else:
                session['user_id'] = user.id
                return redirect(url_for('index'))
        else:
            form.username.errors.append("Nom d'utilisateur inconnu")

    return render_template('login.html', form=form)

@users_api.route("/register", methods=['GET', 'POST'])
def register():
    form = forms.User(request.form)
    if request.method == "POST" and form.validate():
        user = models.User(
            username=form.username.data,
            password=crypt(form.password.data, "s3c3tS4lT"),
            email=form.email.data,
        )
        try:
            user.insert()
        except psycopg2.IntegrityError as e:
            if "(username)" in str(e):
                form.username.errors.append("Ce nom d'utilisateur est déjà pris")
            if "(email)" in str(e):
                form.email.errors.append("Cet email est déjà utilisé par un autre utilisateur")
        else:
            session['user_id'] = user.id
            return redirect(url_for('index'))
    return render_template('register.html', form=form)

@users_api.route("/<int:pk>")
def profile(pk):
    query = "SELECT * FROM users WHERE id=%s"
    user = models.get_or_404(query, [pk], models.User)

    related_query = """
    SELECT {} FROM users WHERE users.id !=%s AND users.id IN (
        SELECT user_id FROM comment WHERE etablissement_id
            IN (
                SELECT etablissement_id FROM comment WHERE
                    user_id=(SELECT id FROM users WHERE id=%s)
                    AND score > 3
            )
            AND score > 3
            GROUP BY user_id
            HAVING COUNT(*) >= 3
    )"""
    related = models.list_of(related_query.format(models.User.star()), [pk, pk], models.User)

    return render_template('profile.html', profile=user, related=related)

@users_api.route("/<int:pk>/set_admin")
@admin_required
def set_admin(pk):
    query = "SELECT * FROM users WHERE id=%s"
    user = models.get_or_404(query, [pk], models.User)
    user.is_admin = True
    user.update()
    return redirect("/users/" + str(user.id))

@users_api.route("/<int:pk>/unset_admin")
@admin_required
def unset_admin(pk):
    if pk == g.user.id:
        return abort(401)
    query = "SELECT * FROM users WHERE id=%s"
    user = models.get_or_404(query, [pk], models.User)
    user.is_admin = False
    user.update()
    return redirect("/users/" + str(user.id))


@users_api.route("/logout")
def logout():
    if "user_id" in session:
        del session['user_id']
    return redirect(url_for('index'))

@users_api.route("/")
def list_users():
    query = "SELECT {} FROM users ORDER BY users.id DESC".format(models.User.star())
    users = models.list_of(query, [], models.User)

    return render_template('list_users.html', users=users)
