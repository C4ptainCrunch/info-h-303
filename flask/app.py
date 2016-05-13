from flask import Flask, render_template, request, g, redirect, url_for, session, abort, flash, jsonify, json, Response, Markup
from functools import wraps
import psycopg2
import psycopg2.extras
from flask_bootstrap import Bootstrap
import forms
import config
import models
from datetime import datetime
import statistics
import humanize
from datetime import date, timedelta
import markdown

from ressources import *

from hotels import hotels_api
from bars import bars_api
from restaurants import restaurants_api
from users import users_api
from tags import tags_api
from comment import comment_api

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
app.register_blueprint(users_api, url_prefix='/users')
app.register_blueprint(tags_api, url_prefix='/tags')
app.register_blueprint(comment_api, url_prefix='/comment')

@app.route("/")
def index():
    query = """
    SELECT etablissement.*, AVG(comment.score) AS score FROM etablissement 
    JOIN comment ON etablissement.id = comment.etablissement_id 
    GROUP BY etablissement.id 
    HAVING COUNT(*) >=3 
    ORDER BY avg(score);
    """
    g.cursor.execute(query)
    rows = g.cursor.fetchall()
    etablissements = []
    for row in rows:
        avg = row["score"]
        e = models.Etablissement.from_dict(row)
        etablissements.append((e, avg))

    return render_template('index.html', top5=etablissements)


@app.route("/search")
def search():
    s = request.args.get("term")
    if s is None:
        return redirect(url_for('index'))
    s = s.strip()

    query = "SELECT * FROM etablissement WHERE SIMILARITY(name, %s) > 0.07 ORDER BY SIMILARITY(name, %s) DESC"
    results = models.list_of(query, [s,s], models.Etablissement)

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


@app.route("/etablissements/<int:pk>")
def get_etablissement(pk):
    query = "SELECT {} FROM etablissement WHERE id=%s".format(models.Etablissement.star())
    e = models.get_or_404(query, [pk], models.Etablissement)

    return redirect("/{}s/{}".format(e.type, e.id))


@app.template_filter('humanize_date')
def humanize_date(d):
    humanize.i18n.activate('fr')
    diff = date.today() - d
    if(diff < timedelta(hours=24)):
        return "aujourd'hui"

    return humanize.naturaltime(diff)

@app.template_filter('markdown')
def markdown_f(string):
    return Markup(markdown.markdown(string))

if __name__ == "__main__":
    app.run(debug=config.DEBUG)
