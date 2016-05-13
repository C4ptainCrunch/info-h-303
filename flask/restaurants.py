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

    day = (datetime.now().isoweekday() - 1)
    is_supper = datetime.now().hour > 15
    return render_template(
        "list_restaurants.html",
        etablissements=restaurants,
        day=day,
        is_supper=is_supper,
    )

@restaurants_api.route("/add", methods=['GET', 'POST'])
@admin_required
def add_restaurant():
    form = forms.Restaurant(request.form)
    if request.method == 'POST' and form.validate():
        print(form.openings.data)
        restaurant = models.Restaurant()
        restaurant.etablissement = models.Etablissement(created=datetime.now(), type="restaurant", user_id=g.user.id)
        form.populate_obj(restaurant)

        openings = [False] * 14
        for d in form.openings.data:
            openings[forms.list_of_days.index(d)] = True
        restaurant.openings = openings

        restaurant.etablissement.insert(g.cursor)
        restaurant.etablissement_id = restaurant.etablissement.id

        restaurant.insert(g.cursor)

        return redirect(url_for('.show_restaurant', etablissement_id=restaurant.etablissement.id))

    return render_template('add_restaurant.html', form=form)

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
    tags = etablissement.get_labels(etablissement_id, g.user.id)
    comments = etablissement.get_comments(etablissement_id)

    return render_template(
        'view_restaurant.html',
        restaurant=restaurant,
        e=restaurant.etablissement,
        tags=tags,
        comments=comments
    )

@restaurants_api.route("/<int:etablissement_id>/edit", methods=['GET', 'POST'])
@admin_required
def edit_restaurant(etablissement_id):
    query = """
    SELECT {}, {}, {} FROM restaurant
    JOIN etablissement ON restaurant.etablissement_id = etablissement.id
    JOIN users ON etablissement.user_id = users.id
    WHERE restaurant.etablissement_id=%s AND etablissement.type='restaurant'
    """.format(models.Etablissement.star(), models.User.star(), models.Restaurant.star())

    g.cursor.execute(query, [etablissement_id])
    data = g.cursor.fetchone()
    restaurant = models.Restaurant.from_dict(data)
    if not data:
        return  abort(404)

    form = forms.Restaurant(request.form, obj=restaurant)
    form.openings.data = [forms.list_of_days[i[0]] for i in enumerate(restaurant.openings) if i[1]]
    if request.method == 'POST' and form.validate():
        form.populate_obj(restaurant)

        openings = [False] * 14
        for d in form.openings.data:
            openings[forms.list_of_days.index(d)] = True
        restaurant.openings = openings

        restaurant.etablissement.update(g.cursor)
        restaurant.update(g.cursor)
        return redirect(url_for('.show_restaurant', etablissement_id=restaurant.etablissement.id))

    return render_template('add_restaurant.html', form=form)
