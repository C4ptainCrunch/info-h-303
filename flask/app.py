from flask import Flask, render_template, request, g
import psycopg2
import psycopg2.extras
from flask_bootstrap import Bootstrap
import forms
import config

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
        return redirect(url_for('login'))
        pass # insert

    return render_template('add_hotel.html', form=form)


if __name__ == "__main__":
    app.run(debug=config.DEBUG)
