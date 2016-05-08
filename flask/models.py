from datetime import datetime

class Model:

    def tablename(self):
        return self.Meta.table

    def non_auto_fields(self):
        return [f for f in self.Meta.fields if f not in self.Meta.auto_fields]

    def __iter__(self):
        return (getattr(self, col) for col in self.non_auto_fields())

    def insert(self, cursor):
        query = 'INSERT INTO %s (%s) VALUES (%s)' % (
                self.tablename(),
                ','.join(self.non_auto_fields()),
                ','.join(['%s']*len(self.non_auto_fields())))

        cursor.execute(query, list(self))
        if self.Meta.pk in self.Meta.auto_fields:
            cursor.execute("SELECT LASTVAL() FROM %s" % self.tablename())
            pk = cursor.fetchone()[0]
            setattr(self, self.Meta.pk, pk)

    def update(self, cursor):
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
        if self.created is None:
            self.created = datetime.now()
        self.created = created
        self.is_admin = is_admin

    def is_authenticated(self):
        return True

    class Meta:
        fields = ['id', "username", "email", "password", "created", "is_admin"]
        auto_fields = ['id']
        pk = 'id'
        table = 'users'
        foreign_models = []


class AnonymousUser:
    def is_authenticated(self):
        return False


class Etablissement(Model):
    def __init__(self, id=None, name=None, phone=None, url=None, address_street=None, address_number=None, address_city=None, address_zip=None, latitude=None, longitude=None, created=None, user_id=None, type=None, picture=None):
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
            address_street=form.street.data,
            address_number=form.number.data,
            address_city=form.city.data,
            address_zip=form.zip.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            created=datetime.now(),
            user_id=user_id,
            type=type,
            picture=form.image.data,
        )
        return instance


    class Meta:
        fields = ['id', "name", "phone", "url", "address_street", "address_number", "address_zip", "address_city", "latitude", "longitude", "created", "user_id", "type", "picture"]
        auto_fields = ['id']
        pk = 'id'
        table = 'etablissement'
        foreign_models = [User]

class Hotel(Model):
    def __init__(self, etablissement_id=None, stars=None, rooms=None, price=None):
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
    def __init__(self, etablissement_id=None, smoker=None, food=None):
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
    def __init__(self, etablissement_id=None, price_range=None, max_seats=None, takeaway=False, delivery=None, openings=None):
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

