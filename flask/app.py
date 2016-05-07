from flask import Flask, render_template, request, g, redirect, url_for
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
def before_request():
    g.db = connect_db()
    g.cursor = g.db.cursor()

@app.teardown_request
def teardown_request(exception):
    cursor = getattr(g, 'cursor', None)
    if cursor is not None:
        cursor.close()

    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/hotels/add", methods=['GET', 'POST'])
def add_hotel():
    form = forms.Hotel(request.form)
    if request.method == 'POST' and form.validate():
        etablissement = models.Etablissement.from_form(form, 1, "hotel")
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

@app.route("/hotels/<etablissement_id>")
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


if __name__ == "__main__":
    app.run(debug=config.DEBUG)
