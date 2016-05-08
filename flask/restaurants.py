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

restaurants_api = Blueprint('restaurants_api', __name__)

@restaurants_api.route("/")
def list_restaurants():
    query = """select {}, {}, avg(comment.score) as score
    from restaurant inner join etablissement on restaurant.etablissement_id = etablissement.id
    left join comment on etablissement.id = comment.etablissement_id
    group by etablissement.id, restaurant.etablissement_id
    ORDER BY score DESC NULLS LAST
    """.format(models.Restaurant.star(), models.Etablissement.star())
    g.cursor.execute(query)
    rows = g.cursor.fetchall()
    restaurants = []
    for row in rows:
        restaurant = models.Restaurant.from_dict(row)
        score = row["score"]
        restaurants.append((restaurant, score))
    return render_template("list_restaurants.html", etablissements=restaurants)

@restaurants_api.route("/<int:etablissement_id>")
def show_restaurant(etablissement_id):
    query = """
    SELECT {}, {}, {} FROM restaurant
    JOIN etablissement ON restaurant.etablissement_id = etablissement.id
    JOIN users ON etablissement.user_id = users.id
    WHERE restaurant.etablissement_id=%s AND etablissement.type='restaurant'
    """.format(models.Etablissement.star(), models.User.star(), models.Restaurant.star())

    g.cursor.execute(query, [etablissement_id])
    data = g.cursor.fetchone()
    if not data:
        return  abort(404)

    restaurant = models.Restaurant.from_dict(data)

    return render_template('view_restaurant.html', restaurant=restaurant, e=restaurant.etablissement)
