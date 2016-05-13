from datetime import datetime
from flask import g, abort
from werkzeug import secure_filename
import os
import urllib, hashlib

class Model:

    def tablename(self):
        return self.Meta.table

    def non_auto_fields(self):
        return [f for f in self.Meta.fields if f not in self.Meta.auto_fields]

    def __iter__(self):
        return (getattr(self, col) for col in self.non_auto_fields())

    def insert(self, cursor=None):
        if cursor is None:
            cursor = g.cursor
        query = 'INSERT INTO %s (%s) VALUES (%s)' % (
                self.tablename(),
                ','.join(self.non_auto_fields()),
                ','.join(['%s']*len(self.non_auto_fields())))

        cursor.execute(query, list(self))
        if self.Meta.pk in self.Meta.auto_fields:
            cursor.execute("SELECT LASTVAL() FROM %s" % self.tablename())
            pk = cursor.fetchone()[0]
            setattr(self, self.Meta.pk, pk)

    def update(self, cursor=None):
        if cursor is None:
            cursor = g.cursor
        params = ', '.join(["{}=%s".format(field) for field in self.non_auto_fields()])
        cursor.execute(
            "UPDATE %s SET %s WHERE %s=%%s" % (self.tablename(), params, self.Meta.pk),
            list(self) + [self.pk]
        )

    @property
    def pk(self):
        return getattr(self, self.Meta.pk)


    @classmethod
    def from_dict(klass, d, is_top=True):
        our_fields = {
            k.split(".")[-1]:v for k,v in d.items()
            if k.startswith(klass.tablename(klass) + ".") or '.' not in k and is_top
        }
        instance = klass(**our_fields)
        for submodel in klass.Meta.foreign_models:
            try:
                submodel_instance = submodel.from_dict(d, is_top=False)
            except Exception as e:
                submodel_instance = None
                print(e)
            setattr(instance, submodel.__name__.lower(), submodel_instance)

        return instance

    @classmethod
    def star(klass):
        return ','.join(['{0}.{1} AS "{0}.{1}"'.format(klass.Meta.table, col) for col in klass.Meta.fields])



class Label(Model):
    def __init__(self, id=None, name=None):
        self.id = int(id) if id is not None else None
        self.name = name


    class Meta:
        fields = ['id', 'name']
        auto_fields = ['id']
        pk = 'id'
        table = 'label'
        foreign_models = []


class User(Model):
    def __init__(self, id=None, username=None, email=None, password=None, created=None, is_admin=False):
        self.id = int(id) if id is not None else None
        self.username = username
        self.email = email
        self.password = password
        if created is None:
            created = datetime.now()
        self.created = created
        self.is_admin = is_admin

    def is_authenticated(self):
        return True

    def gravatar(self):
        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(self.email.lower().encode('utf-8')).hexdigest() + "?"
        gravatar_url += urllib.parse.urlencode({'d':'wavatar', 's':str(100)})
        return gravatar_url

    class Meta:
        fields = ['id', "username", "email", "password", "created", "is_admin"]
        auto_fields = ['id']
        pk = 'id'
        table = 'users'
        foreign_models = []


class AnonymousUser:
    def is_authenticated(self):
        return False

    @property
    def is_admin(self):
        return False

    @property
    def id(self):
        return -1



class Etablissement(Model):
    def __init__(self, id=None, name=None, phone=None, url=None, address_street=None, address_number=None, address_city=None, address_zip=None, latitude=None, longitude=None, created=None, user_id=None, type=None, picture=None, *args, **kwargs):
        self.id = int(id) if id is not None else None
        self.name = name
        self.phone = phone
        self.url = url
        self.address_street = address_street
        self.address_number = address_number
        self.address_city = address_city
        self.address_zip = address_zip
        self.latitude = latitude
        self.longitude = longitude
        self.created = created
        self.user_id = user_id
        self.type = type
        self.picture = picture

    @classmethod
    def from_form(klass, form, user_id, type):
        instance = klass(
            name=form.name.data,
            phone=form.phone.data,
            url=form.url.data,
            address_street=form.address_street.data,
            address_number=form.address_number.data,
            address_city=form.address_city.data,
            address_zip=form.address_zip.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            created=datetime.now(),
            user_id=user_id,
            type=type,
        )
        return instance

    def to_marker(self):
        return {
            "name": self.name,
            "lat": float(self.latitude),
            "lon": float(self.longitude),
        }

    def set_picture(self, form_field, files):
        image = files[form_field.name]
        if image:
            image_data = image.read()
            secure = secure_filename(image.filename)
            open('static/media/' + secure, 'wb').write(image_data)
            self.picture = '/static/media/' + secure

    def get_picture(self):
        if self.picture:
            return self.picture

        if self.type == 'hotel':
            return "/static/default-hotel.jpg"

        if self.type == 'bar':
            return "/static/default-bar.jpg"

        if self.type == 'restaurant':
            return "/static/default-restaurant.jpg"

    def get_url(self):
        if self.type == 'hotel':
            return "/hotels/" + str(self.id)

        if self.type == 'bar':
            return "/bars/" + str(self.id)

        if self.type == 'restaurant':
            return "/restaurants/" + str(self.id)

    class Meta:
        fields = ['id', "name", "phone", "url", "address_street", "address_number", "address_zip", "address_city", "latitude", "longitude", "created", "user_id", "type", "picture"]
        auto_fields = ['id']
        pk = 'id'
        table = 'etablissement'
        foreign_models = [User]

class Hotel(Model):
    def __init__(self, etablissement_id=None, stars=None, rooms=None, price=None, *args, **kwargs):
        self.etablissement_id = etablissement_id
        self.stars = stars
        self.rooms = rooms
        self.price = price

    class Meta:
        fields = ["etablissement_id", "stars", "rooms", "price"]
        auto_fields = []
        pk = 'etablissement_id'
        table = 'hotel'
        foreign_models = [Etablissement]


class Bar(Model):
    def __init__(self, etablissement_id=None, smoker=None, food=None, *args, **kwargs):
        self.etablissement_id = etablissement_id
        self.smoker = smoker
        self.food = food

    class Meta:
        fields = ["etablissement_id","smoker","food",]
        auto_fields = []
        pk = 'etablissement_id'
        table = 'bar'
        foreign_models = [Etablissement]


class Restaurant(Model):
    def __init__(self, etablissement_id=None, price_range=None, max_seats=None, takeaway=False, delivery=None, openings=None, *args, **kwargs):
        self.etablissement_id = etablissement_id
        self.price_range = price_range
        self.max_seats = max_seats
        self.takeaway = takeaway
        self.delivery = delivery
        self.openings = openings

    class Meta:
        fields = ["etablissement_id", "price_range", "max_seats", "takeaway", "delivery", "openings"]
        auto_fields = []
        pk = 'etablissement_id'
        table = 'restaurant'
        foreign_models = [Etablissement]



def get_or_404(query, params, model):
    g.cursor.execute(query, params)
    row = g.cursor.fetchone()
    if row is None:
        return abort(404)
    return model.from_dict(row)


def list_of(query, params, model):
    g.cursor.execute(query, params)
    rows = g.cursor.fetchall()
    def map_to_model(r):
        m = model.from_dict(r)
        m.extra = r
        return m
    return [map_to_model(r) for r in rows]
