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
