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
import models

from ressources import *

def get_labels(etablissement_id, user_id):
    query = """
        SELECT {}, NOT BOOL_AND(user_id != %s) AS was_tagged_by_user
        FROM etablissement_label
        JOIN label ON label.id = etablissement_label.label_id
        WHERE etablissement_label.etablissement_id = %s
        GROUP BY label.id
    """.format(models.Label.star())

    g.cursor.execute(query, [user_id, etablissement_id])
    return g.cursor.fetchall()

def get_comments(etablissement_id):
    query = """
    SELECT {}, {} FROM comment
    JOIN users
        ON comment.user_id=users.id
    WHERE comment.etablissement_id=%s
    ORDER BY date DESC, comment.id DESC
    """.format(models.Comment.star(), models.User.star())

    return models.list_of(query, [etablissement_id], models.Comment)

