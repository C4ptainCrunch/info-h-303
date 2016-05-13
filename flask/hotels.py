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
import etablissement

from ressources import *

hotels_api = Blueprint('hotels_api', __name__)

@hotels_api.route("/")
def list_hotels():
    query = """select {}, {}, avg(comment.score) as score
    from hotel inner join etablissement on hotel.etablissement_id = etablissement.id
    left join comment on etablissement.id = comment.etablissement_id
    group by etablissement.id, hotel.etablissement_id
    ORDER BY score DESC NULLS LAST
    """.format(models.Hotel.star(), models.Etablissement.star())
    g.cursor.execute(query)
    rows = g.cursor.fetchall()
    hotels = []
    for row in rows:
        hotel = models.Hotel.from_dict(row)
        score = row["score"]
        hotels.append((hotel, score))

    return render_template("list_hotels.html", etablissements=hotels)

@hotels_api.route("/add", methods=['GET', 'POST'])
@admin_required
def add_hotel():
    form = forms.Hotel(request.form)
    if request.method == 'POST' and form.validate():
        hotel = models.Hotel()
        hotel.etablissement = models.Etablissement(created=datetime.now(), type="hotel", user_id=g.user.id)
        form.populate_obj(hotel)

        hotel.etablissement.insert(g.cursor)
        hotel.etablissement_id = hotel.etablissement.id
        hotel.etablissement.set_picture(form.etablissement.picture, request.files)

        hotel.insert(g.cursor)

        return redirect(url_for('.show_hotel', etablissement_id=hotel.etablissement.id))

    return render_template('add_hotel.html', form=form)

@hotels_api.route("/<int:etablissement_id>")
def show_hotel(etablissement_id):
    query = """
    SELECT {}, {}, {} FROM hotel
    JOIN etablissement ON hotel.etablissement_id = etablissement.id
    JOIN users ON etablissement.user_id = users.id
    WHERE hotel.etablissement_id=%s AND etablissement.type='hotel'
    """.format(models.Etablissement.star(), models.User.star(), models.Hotel.star())

    g.cursor.execute(query, [etablissement_id])
    data = g.cursor.fetchone()
    if not data:
        return  abort(404)

    hotel = models.Hotel.from_dict(data)
    tags = etablissement.get_labels(etablissement_id, g.user.id)
    comments = etablissement.get_comments(etablissement_id)

    return render_template('view_hotel.html', hotel=hotel, e=hotel.etablissement, tags=tags, comments=comments, commentForm=forms.Comment(), should_comment=(len(list(filter(lambda x:x.user_id == g.user.id and x.date == date.today(), comments))) == 0))

@hotels_api.route("/<int:etablissement_id>/edit", methods=['GET', 'POST'])
@admin_required
def edit_hotel(etablissement_id):
    query = """
    SELECT {}, {}, {} FROM hotel
    JOIN etablissement ON hotel.etablissement_id = etablissement.id
    JOIN users ON etablissement.user_id = users.id
    WHERE hotel.etablissement_id=%s AND etablissement.type='hotel'
    """.format(models.Etablissement.star(), models.User.star(), models.Hotel.star())

    g.cursor.execute(query, [etablissement_id])
    data = g.cursor.fetchone()
    if not data:
        return  abort(404)
    hotel = models.Hotel.from_dict(data)
    image = hotel.etablissement.picture


    form = forms.Hotel(request.form, obj=hotel)
    if request.method == 'POST' and form.validate():
        form.populate_obj(hotel)
        hotel.etablissement.picture = image
        hotel.etablissement.set_picture(form.etablissement.picture, request.files)
        hotel.etablissement.update(g.cursor)
        hotel.update(g.cursor)
        return redirect(url_for('.show_hotel', etablissement_id=hotel.etablissement.id))


    return render_template('add_hotel.html', form=form)
