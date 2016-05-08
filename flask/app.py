from flask import Flask, render_template, request, g, redirect, url_for, session, abort, flash, jsonify, json, Response
from functools import wraps
import psycopg2
import psycopg2.extras
from flask_bootstrap import Bootstrap
import forms
import config
import models
from datetime import datetime
import statistics

app = Flask(__name__)
app.secret_key = 's3cr3t'
Bootstrap(app)

def connect_db():
    conn = psycopg2.connect(config.DB_URL, cursor_factory=psycopg2.extras.DictCursor)
    conn.autocommit = True
    return conn

@app.before_request
def open_db():
    g.db = connect_db()
    g.cursor = g.db.cursor()

@app.before_request
def get_user_cookie():
    if "user_id" in session:
        query = "SELECT * FROM users WHERE id=%s"
        g.cursor.execute(query, [session['user_id']])
        user = models.User.from_dict(g.cursor.fetchone())
        g.user = user
    else:
        g.user = models.AnonymousUser()

@app.teardown_request
def close_db(exception):
    cursor = getattr(g, 'cursor', None)
    if cursor is not None:
        cursor.close()

    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

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
        if g.user.is_admin:
            return fn(*args, **kwargs)
        else:
            return abort(403)
    return outer

@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403

@app.context_processor
def inject_user():
    return dict(user=g.user)

@app.route("/")
def index():
    query = "SELECT etablissement.*, AVG(comment.score) AS score FROM etablissement LEFT JOIN comment ON etablissement.id = comment.etablissement_id GROUP BY etablissement.id ORDER BY AVG(comment.score) DESC NULLS LAST"
    g.cursor.execute(query)
    rows = g.cursor.fetchall()
    etablissements = []
    for row in rows:
        avg = row["score"]
        e = models.Etablissement.from_dict(row)
        etablissements.append((e, avg))

    return render_template('index.html', top5=etablissements[:5])


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = forms.Login(request.form)
    if request.method == "POST" and form.validate():
        query = "SELECT * FROM users WHERE username=%s"
        g.cursor.execute(query, [form.username.data])
        row = g.cursor.fetchone()
        if row:
            user = models.User.from_dict(row)
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            form.username.errors.append("Nom d'utilisateur ou mot de passe invalide")
            form.password.errors.append("Nom d'utilisateur ou mot de passe invalide")

    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session['user_id']
    return redirect(url_for('index'))


@app.route("/hotels")
def list_hotels():
    query = """select {}, {}, avg(comment.score) as score
    from hotel inner join etablissement on hotel.etablissement_id = etablissement.id
    left join comment on etablissement.id = comment.etablissement_id
    group by etablissement.id, hotel.etablissement_id
    ORDER BY score DESC NULLS LAST
    """.format(models.Hotel.star(), models.Etablissement.star())
    g.cursor.execute(query)
    rows = g.cursor.fetchall()
    hotels = []
    for row in rows:
        hotel = models.Hotel.from_dict(row)
        score = row["score"]
        hotels.append((hotel, score))
    return render_template("list_hotels.html", etablissements=hotels)

@app.route("/hotels/add", methods=['GET', 'POST'])
@admin_required
def add_hotel():
    form = forms.Hotel(request.form)
    if request.method == 'POST' and form.validate():
        etablissement = models.Etablissement.from_form(form, g.user.id, "hotel")
        etablissement.insert(g.cursor)

        hotel = models.Hotel(
            etablissement_id=etablissement.id,
            stars=form.stars.data,
            rooms=form.rooms.data,
            price=form.price.data
        )
        hotel.insert(g.cursor)

        return redirect(url_for('show_hotel', etablissement_id=etablissement.id))

    return render_template('add_hotel.html', form=form)

@app.route("/hotels/<int:etablissement_id>")
def show_hotel(etablissement_id):
    query = """
    SELECT {}, {}, {} FROM hotel
    JOIN etablissement ON hotel.etablissement_id = etablissement.id
    JOIN users ON etablissement.user_id = users.id
    WHERE hotel.etablissement_id=%s AND etablissement.type='hotel'
    """.format(models.Etablissement.star(), models.User.star(), models.Hotel.star())

    g.cursor.execute(query, [etablissement_id])
    data = g.cursor.fetchone()
    if not data:
        return  abort(404)

    hotel = models.Hotel.from_dict(data)

    return render_template('view_hotel.html', hotel=hotel, e=hotel.etablissement)

@app.route("/bars")
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

@app.route("/bars/<int:etablissement_id>")
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

@app.route("/restaurants")
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

@app.route("/restaurants/<int:etablissement_id>")
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

@app.route("/search")
def search():
    s = request.args.get("term")
    if s is None:
        return redirect(url_for('index'))
    query = "SELECT * FROM etablissement WHERE SIMILARITY(name, %s) > 0.07 ORDER BY SIMILARITY(name, %s) DESC"
    s = s.strip()
    g.cursor.execute(query, [s,s])
    results = [models.Etablissement.from_dict(row) for row in g.cursor.fetchall()]
    if len(results) == 1:
        e = results[0]
        return redirect("/{}s/{}".format(e.type, e.id))
    js = {}
    if results:
        js = {
            "center": [
                float(statistics.mean([r.latitude for r in results])),
                float(statistics.mean([r.longitude for r in results])),
            ],
            "points": [r.to_marker() for r in results]
        }

    return render_template('search.html', term=s, results=results, searchdata=json.dumps(js))

@app.route("/random")
def random():
    query = "SELECT id, type FROM etablissement ORDER BY RANDOM() LIMIT 1"
    g.cursor.execute(query)
    row = g.cursor.fetchone()

    return redirect("/{}s/{}".format(row['type'], row['id']))

@app.route("/delete/<int:etablissement_id>")
@admin_required
def delete(etablissement_id):
    query = "DELETE FROM etablissement WHERE id=%s"
    g.cursor.execute(query, [etablissement_id])
    return redirect("/")


@app.route("/api/etablissemens/all")
def api_all():
    query = "SELECT * FROM etablissement"
    g.cursor.execute(query)
    l = [models.Etablissement.from_dict(e).to_marker() for e in g.cursor.fetchall()]
    return Response(response=json.dumps(l),
                    status=200,
                    mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=config.DEBUG)
