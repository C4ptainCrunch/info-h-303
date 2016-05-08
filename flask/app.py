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

from ressources import *

from hotels import hotels_api
from bars import bars_api
from restaurants import restaurants_api

app = Flask(__name__)
app.secret_key = 's3cr3t'
Bootstrap(app)


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

@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403

@app.context_processor
def inject_user():
    return dict(user=g.user)

app.register_blueprint(hotels_api, url_prefix='/hotels')
app.register_blueprint(bars_api, url_prefix='/bars')
app.register_blueprint(restaurants_api, url_prefix='/restaurants')

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
