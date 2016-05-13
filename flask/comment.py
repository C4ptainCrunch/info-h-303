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

@comment_api.route("/edit/<int:cid>", methods=["GET", "POST"])
@auth_required
def edit_comment(cid):
    query = """
    SELECT {} FROM comment
    WHERE comment.id=%s
    """.format(models.Comment.star())

    g.cursor.execute(query, [cid])
    data = g.cursor.fetchone()
    if not data:
        return  abort(404)
    comment = models.Comment.from_dict(data)
    uid = comment.user_id
    epk = comment.etablissement_id
    date = comment.date 

    if g.user.id == uid or g.user.is_admin:
        form = forms.Comment(request.form, obj=comment)
        if request.method == 'POST' and form.validate():
            form.populate_obj(comment)
            comment.user_id = uid
            comment.etablissement_id = epk
            comment.date = data
            comment.update(g.cursor)
            return redirect(url_for('get_etablissement', pk=epk))
    else:
        return abort(401)


    return render_template('edit_user.html', form=form)
