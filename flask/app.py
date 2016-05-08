from flask import Flask, render_template, request, g, redirect, url_for, session, abort, flash, jsonify, json, Response
import psycopg2
import psycopg2.extras
from flask_bootstrap import Bootstrap
import forms
import config
import models
from datetime import datetime

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
    def outer(*args, **kwargs):
        if g.user.is_authenticated():
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
    # raise g.user
    return render_template('index.html')


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


@app.route("/hotels/add", methods=['GET', 'POST'])
@auth_required
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
    WHERE hotel.etablissement_id=%s
    """.format(models.Etablissement.star(), models.User.star(), models.Hotel.star())

    g.cursor.execute(query, [etablissement_id])
    hotel = models.Hotel.from_dict(g.cursor.fetchone())

    return render_template('view_hotel.html', hotel=hotel, e=hotel.etablissement)


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
