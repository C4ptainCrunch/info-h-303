from django.db import models, connection
from django.db.models.fields.related import OneToOneField

class RawModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        cursor = connection.cursor()
        primary = self._meta.pk.column
        table =self._meta.db_table
        add = True
        if self.pk is not None:
            if type(self._meta.pk) != OneToOneField:
                print("type not OneToOneField")
                add = False
            else:
                cursor.execute("""SELECT * from %s WHERE %s = %%s""" % (table, primary) , [self.pk])
                add = cursor.fetchone() is None

        fields = [f for f in self._meta.concrete_fields if not (f.primary_key and type(f) != OneToOneField)]
        data = [f.get_prep_value(f.pre_save(self, add)) for f in fields]

        if not add: # update
            sets = ", ".join(["%s = %%s" % field.column for field in fields])
            params = data + [self.pk]
            query = "UPDATE \"%s\" SET %s WHERE %s = %%s" % (table, sets, primary)
        else: # insert
            columns = ",".join([f.column for f in fields])
            values = ",".join(["%s"] * len(fields))
            params = data
            query = "INSERT INTO \"%s\" (%s) VALUES (%s)" % (table, columns, values)

        cursor.execute(query, params)
        if add:
            cursor.execute('SELECT LASTVAL()')
            pk = cursor.fetchone()[0]
            self.pk = pk

