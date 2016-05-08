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

    return render_template('view_bar.html', bar=bar, e=bar.etablissement)
