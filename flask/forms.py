from flask_wtf import Form
from flask_wtf.html5 import TelField, URLField, IntegerField, DecimalField
from flask_wtf.file import FileField
from wtforms import TextField, TextAreaField, SubmitField, validators, PasswordField

class Etablissement(Form):
    name = TextField('Nom', [validators.Length(min=4, max=254)])
    phone = TelField('Téléphone', [validators.Length(min=6, max=20)])
    url = URLField('Site web') # enmtpy:true

    number = TextField("Numéro", [validators.Length(min=1, max=5)])
    street = TextField("Rue", [validators.Length(min=2, max=254)])
    zip = IntegerField("Code postal")
    city = TextField("Ville", [validators.Length(min=2, max=254)])

    latitude = DecimalField("Latitude", validators=[validators.NumberRange(min=-180, max=180)], places=6)
    longitude = DecimalField("Longitude", validators=[validators.NumberRange(min=-180, max=180)], places=6)

    image = FileField("Photo")



class Hotel(Etablissement):
    stars = IntegerField("Etoiles", validators=[validators.NumberRange(min=0, max=5)])
    rooms = IntegerField("Nombre de chambres", validators=[validators.NumberRange(min=0)])
    price = IntegerField("Prix d'une chambre double", validators=[validators.NumberRange(min=0)])

    submit = SubmitField("Envoyer")

class Login(Form):
    username = TextField("Nom d'utilisateur")
    password = PasswordField('Mot de passe')

    submit = SubmitField("Envoyer")
