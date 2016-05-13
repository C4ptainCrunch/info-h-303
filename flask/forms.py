from flask_wtf import Form
from flask_wtf.html5 import TelField, URLField, IntegerField, DecimalField, EmailField
from flask_wtf.file import FileField
from wtforms import TextField, TextAreaField, SubmitField, validators, PasswordField, FormField, BooleanField, FieldList, Field, SelectMultipleField, widgets
from wtforms import Form as WForm

list_of_days = ['Lu am', 'Lu pm', "Ma am", 'Ma pm', 'Me am', 'Me pm', "Je am", "Je pm", "Ve am", "Ve pm", "Sa am", "Sa pm", "Su am", "Su pm"]


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(html_tag="ul",prefix_label=False)
    option_widget = widgets.CheckboxInput()

    def validate(self, *args, **kwargs):
        return True

class Etablissement(WForm):
    name = TextField('Nom', [validators.Length(min=4, max=254)])
    phone = TelField('Téléphone', [validators.Length(min=6, max=20)])
    url = URLField('Site web') # enmtpy:true

    address_number = TextField("Numéro", [validators.Length(min=1, max=5)])
    address_street = TextField("Rue", [validators.Length(min=2, max=254)])
    address_zip = IntegerField("Code postal")
    address_city = TextField("Ville", [validators.Length(min=2, max=254)])

    latitude = DecimalField("Latitude", validators=[validators.NumberRange(min=-180, max=180)], places=6)
    longitude = DecimalField("Longitude", validators=[validators.NumberRange(min=-180, max=180)], places=6)

    picture = FileField("Photo")



class Hotel(Form):
    etablissement = FormField(Etablissement)
    stars = IntegerField("Etoiles", validators=[validators.NumberRange(min=0, max=5)])
    rooms = IntegerField("Nombre de chambres", validators=[validators.NumberRange(min=0)])
    price = IntegerField("Prix d'une chambre double", validators=[validators.NumberRange(min=0)])

    submit = SubmitField("Envoyer")

class Bar(Form):
    etablissement = FormField(Etablissement)
    smoker = BooleanField("Fumeur")
    food = BooleanField("Petite restauration")

    submit = SubmitField("Envoyer")

class Restaurant(Form):
    etablissement = FormField(Etablissement)
    price_range = IntegerField("Prix d'un repas", validators=[validators.NumberRange(min=0)])
    max_seats = IntegerField("Nombre de places", validators=[validators.NumberRange(min=0)])
    takeaway = BooleanField("À emporter")
    delivery = BooleanField("Livre à domicile")

    days = [(x, x) for x in list_of_days]
    openings = MultiCheckboxField("Jours d'ouverture", choices=days)

    submit = SubmitField("Envoyer")

class Login(Form):
    username = TextField("Nom d'utilisateur")
    password = PasswordField('Mot de passe')

    submit = SubmitField("Envoyer")

class User(Form):
    username = TextField("Nom d'utilisateur")
    email = EmailField("Adresse mail")
    password = PasswordField('Mot de passe', [
        validators.Required(),
        validators.EqualTo('confirm', message='Les mots de passe doivent être identiques')
    ])
    confirm = PasswordField('Mot de passe (à nouveau)')

    submit = SubmitField("Envoyer")

class PasswordUser(Form):
    password = PasswordField('Mot de passe', [
        validators.Required(),
        validators.EqualTo('confirm', message='Les mots de passe doivent être identiques')
    ])
    confirm = PasswordField('Mot de passe (à nouveau)')

    submit = SubmitField("Envoyer")


class EditUser(Form):
    username = TextField("Nom d'utilisateur")
    email = EmailField("Adresse mail")

    submit = SubmitField("Envoyer")
