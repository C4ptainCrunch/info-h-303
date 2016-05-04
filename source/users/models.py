from django.db import models
from horeca.models import RawModel


class User(RawModel):
    REQUIRED_FIELDS = ["email", "password"]
    USERNAME_FIELD = "username"
    username = models.CharField(unique=True, max_length=254)
    email = models.CharField(unique=True, max_length=254)
    password = models.CharField(max_length=128)
    created = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'user'

    def __str__(self):
        return self.username

    def is_authenticated(self):
        return True

class AnonymousUser:
    def is_authenticated(self):
        return False

class Session(RawModel):
    user = models.ForeignKey('users.User', models.CASCADE)
    cookie = models.CharField(unique=True, max_length=128)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'session'

    def __str__(self):
        return "session for %s" % self.user
