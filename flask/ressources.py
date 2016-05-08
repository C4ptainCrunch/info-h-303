from flask import Blueprint, render_template, request, g, redirect, url_for, session, abort, flash, jsonify, json, Response
import psycopg2
import psycopg2.extras
from flask_bootstrap import Bootstrap
import forms
import config
import models
from datetime import datetime
import statistics
from functools import wraps

def auth_required(fn):
    @wraps(fn)
    def outer(*args, **kwargs):
        if g.user.is_authenticated():
            return fn(*args, **kwargs)
        else:
            return abort(403)
    return outer

def admin_required(fn):
    @wraps(fn)
    def outer(*args, **kwargs):
        print(args)
        if g.user.is_admin:
            return fn(*args, **kwargs)
        else:
            return abort(403)
    return outer


def connect_db():
    conn = psycopg2.connect(config.DB_URL, cursor_factory=psycopg2.extras.DictCursor)
    conn.autocommit = True
    return conn
