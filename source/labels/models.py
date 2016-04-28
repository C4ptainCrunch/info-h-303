from django.db import models
from horeca.models import RawModel


class Label(RawModel):
    name = models.CharField(unique=True, max_length=254)
    users = models.ManyToManyField("users.User", through='EtablissementLabel')

    class Meta:
        managed = False
        db_table = 'label'

    def __str__(self):
        return self.name

class EtablissementLabel(RawModel):
    etablissement = models.ForeignKey("etablissements.Etablissement", models.CASCADE)
    user = models.ForeignKey('users.User', models.CASCADE)
    label = models.ForeignKey('Label', models.CASCADE)

    class Meta:
        managed = False
        db_table = 'etablissement_label'
        unique_together = (('etablissement', 'user', 'label'),)

    def __str__(self):
        return "%s on %s by %s" % (self.label, self.etablissement, self.user)
