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
            k:v for k,v in d.items()
            if k.startswith(klass.tablename(klass) + ".") or '.' not in k and is_top
        }
        instance = klass(**our_fields)
        for submodel in klass.Meta.foreign_models:
            try:
                submodel_instance = submodel.from_dict(d, is_top=False)
            except:
                submodel_instance = None
            setattr(instance, submodel.__name__.lower(), submodel_instance)

        return instance



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


class Etablissement(Model):
    def __init__(self, id=None, name=None):
        self.id = int(id) if id is not None else None
        self.name = name


    class Meta:
        fields = ['id', "name", "phone", "url", "address_street", "address_number", "address_zip", "address_city", "latitude", "longitude", "created", "user", "type", "picture"]
        auto_fields = ['id']
        pk = 'id'
        table = 'etablissement'
        foreign_models = []

class Hotel(Model):
    def __init__(self, id=None, name=None):
        self.id = int(id) if id is not None else None
        self.name = name


    class Meta:
        fields = ["etablissement_id", "stars", "rooms", "price"]
        auto_fields = []
        pk = 'etablissement_id'
        table = 'hotel'
        foreign_models = [Etablissement]


class Bar(Model):
    def __init__(self, id=None, name=None):
        self.id = int(id) if id is not None else None
        self.name = name


    class Meta:
        fields = ["etablissement_id","smoker","food",]
        auto_fields = []
        pk = 'etablissement_id'
        table = 'bar'
        foreign_models = [Etablissement]


class Restaurant(Model):
    def __init__(self, id=None, name=None):
        self.id = int(id) if id is not None else None
        self.name = name


    class Meta:
        fields = ["etablissement_id", "price_range", "max_seats", "takeaway", "delivery", "openings"]
        auto_fields = []
        pk = 'etablissement_id'
        table = 'restaurant'
        foreign_models = [Etablissement]

