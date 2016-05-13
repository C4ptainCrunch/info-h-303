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
import itertools

from ressources import *

tags_api = Blueprint('tags_api', __name__)

@tags_api.route("/")
def list_tags():
    query = """
    SELECT {}, {}, COUNT(*) AS tag_count
    FROM etablissement_label
        JOIN label ON label.id = etablissement_label.label_id
        JOIN etablissement ON etablissement.id = etablissement_label.etablissement_id
        GROUP BY etablissement.id, label.id
        ORDER BY label.name, tag_count DESC
    """.format(models.Label.star(), models.Etablissement.star())
    g.cursor.execute(query)
    rows = g.cursor.fetchall()
    tags = itertools.groupby(rows, key=lambda x: (x['label.name'], x['label.id']))
    tags = [(group, [(models.Etablissement.from_dict(e), e['tag_count']) for e in data]) for group, data in tags]
    return render_template("list_tags.html", tags=tags)

@tags_api.route("/add/<int:epk>", methods=['GET', 'POST'])
@auth_required
def list_add_tag(epk):
    query = """
    SELECT label.* FROM label
    LEFT JOIN etablissement_label
        ON etablissement_label.label_id=label.id
        AND etablissement_label.user_id=%s
        AND etablissement_label.etablissement_id=%s
    WHERE etablissement_label.label_id IS NULL"""

    sq = "SELECT {} FROM etablissement WHERE id=%s".format(models.Etablissement.star())
    e = models.get_or_404(sq, [epk], models.Etablissement)
    tags = models.list_of(query, [g.user.id, epk], models.Label)
    return render_template("choose_tag.html", e=e, tags=tags)


@tags_api.route("/add/<int:epk>/<int:tid>")
@auth_required
def add_tag(epk, tid):
    query = """
    INSERT INTO etablissement_label
    (etablissement_id, user_id, label_id)
    VALUES (%s, %s, %s)
    """
    g.cursor.execute(query, [epk, g.user.id, tid])
    return redirect("/etablissements/"+ str(epk))


@tags_api.route("/remove/<int:epk>/<int:tid>")
@auth_required
def remove_tag(epk, tid):
    query = """
    DELETE FROM etablissement_label
    WHERE etablissement_id=%s AND user_id=%s AND label_id=%s
    """
    g.cursor.execute(query, [epk, g.user.id, tid])
    return redirect("/etablissements/"+ str(epk))
