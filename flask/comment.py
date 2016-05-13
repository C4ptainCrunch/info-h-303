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

comment_api = Blueprint('comment_api', __name__)

@comment_api.route("/add/<int:epk>/<int:uid>", methods=["POST"])
@auth_required
def add_comment(epk, uid):
    form = forms.Comment(request.form)
    if request.method == 'POST' and form.validate():
        comment = models.Comment()
        form.populate_obj(comment)

        comment.user_id = uid
        comment.etablissement_id = epk
        comment.date = datetime.now().date()
        comment.insert(g.cursor)

        return redirect(url_for('get_etablissement', pk=epk))

    return render_template('add_hotel.html', form=form)