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

bars_api = Blueprint('bars_api', __name__)


@bars_api.route("/")
def list_bars():
    query = """select {}, {}, avg(comment.score) as score
    from bar inner join etablissement on bar.etablissement_id = etablissement.id
    left join comment on etablissement.id = comment.etablissement_id
    group by etablissement.id, bar.etablissement_id
    ORDER BY score DESC NULLS LAST
    """.format(models.Bar.star(), models.Etablissement.star())
    g.cursor.execute(query)
    rows = g.cursor.fetchall()
    bars = []
    for row in rows:
        bar = models.Bar.from_dict(row)
        score = row["score"]
        bars.append((bar, score))
    return render_template("list_bars.html", etablissements=bars)

@bars_api.route("/add", methods=['GET', 'POST'])
@admin_required
def add_bar():
    form = forms.Bar(request.form)
    if request.method == 'POST' and form.validate():
        bar = models.Bar()
        bar.etablissement = models.Etablissement(created=datetime.now(), type="bar", user_id=g.user.id)
        form.populate_obj(bar)
        bar.etablissement.set_picture(form.etablissement.picture, request.files)

        bar.etablissement.insert(g.cursor)
        bar.etablissement_id = bar.etablissement.id

        bar.insert(g.cursor)

        return redirect(url_for('.show_bar', etablissement_id=bar.etablissement.id))

    return render_template('add_hotel.html', form=form)

@bars_api.route("/<int:etablissement_id>")
def show_bar(etablissement_id):
    query = """
    SELECT {}, {}, {} FROM bar
    JOIN etablissement ON bar.etablissement_id = etablissement.id
    JOIN users ON etablissement.user_id = users.id
    WHERE bar.etablissement_id=%s AND etablissement.type='bar'
    """.format(models.Etablissement.star(), models.User.star(), models.Bar.star())

    g.cursor.execute(query, [etablissement_id])
    data = g.cursor.fetchone()
    if not data:
        return  abort(404)

    bar = models.Bar.from_dict(data)
    tags = etablissement.get_labels(etablissement_id, g.user.id)

    return render_template('view_bar.html', bar=bar, e=bar.etablissement, tags=tags)

@bars_api.route("/<int:etablissement_id>/edit", methods=['GET', 'POST'])
@admin_required
def edit_bar(etablissement_id):
    query = """
    SELECT {}, {}, {} FROM bar
    JOIN etablissement ON bar.etablissement_id = etablissement.id
    JOIN users ON etablissement.user_id = users.id
    WHERE bar.etablissement_id=%s AND etablissement.type='bar'
    """.format(models.Etablissement.star(), models.User.star(), models.Bar.star())

    g.cursor.execute(query, [etablissement_id])
    data = g.cursor.fetchone()
    if not data:
        return  abort(404)
    bar = models.Bar.from_dict(data)
    image = bar.etablissement.picture

    form = forms.Bar(request.form, obj=bar)
    if request.method == 'POST' and form.validate():
        form.populate_obj(bar)
        bar.etablissement.picture = image
        bar.etablissement.set_picture(form.etablissement.picture, request.files)
        bar.etablissement.update(g.cursor)
        bar.update(g.cursor)
        return redirect(url_for('.show_bar', etablissement_id=bar.etablissement.id))

    return render_template('add_hotel.html', form=form)
