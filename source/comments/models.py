from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from horeca.models import RawModel

class Comment(RawModel):
    user = models.ForeignKey('users.User', models.CASCADE)
    etablissement = models.ForeignKey('etablissements.Etablissement', models.CASCADE)
    date = models.DateField(auto_now_add=True)
    score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    text = models.TextField()

    class Meta:
        managed = False
        db_table = 'comment'
        unique_together = (('date', 'user'),)

    def __str__(self):
        return "%s on %s (%i stars)" % (self.user, self.etablissement, self.score)
