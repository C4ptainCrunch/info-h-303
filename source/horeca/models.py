from django.db import models, connection

class RawModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        add = self.pk is None

        primary = self._meta.pk.column
        fields = [f for f in self._meta.concrete_fields if not f.primary_key]
        data = [f.get_prep_value(f.pre_save(self, add)) for f in fields]
        table =self._meta.db_table

        if not add: # update
            sets = ", ".join(["%s = %%s" % field.column for field in fields])
            params = data + [self.pk]
            query = "UPDATE \"%s\" SET %s WHERE %s = %%s" % (table, sets, primary)
        else: # insert
            columns = ",".join([f.column for f in fields])
            values = ",".join(["%s"] * len(fields))
            params = data
            query = "INSERT INTO \"%s\" (%s) VALUES (%s)" % (table, columns, values)

        cursor = connection.cursor()
        cursor.execute(query, params)
        if add:
            cursor.execute('SELECT LASTVAL()')
            pk = cursor.fetchone()[0]
            self.pk = pk

