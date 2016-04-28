from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from horeca.models import RawModel


class Etablissement(RawModel):
    TYPES_CHOICES = (
        ('restaurant', 'Restaurant'),
        ('hotel', 'Hotel'),
        ('bar', 'Bar'),
    )

    name = models.CharField(max_length=254)
    phone = models.CharField(max_length=20)
    url = models.URLField(blank=True, null=True)
    address_street = models.CharField(max_length=254)
    address_number = models.IntegerField(validators=[MinValueValidator(0)])
    address_zip = models.IntegerField(validators=[MinValueValidator(0)])
    address_city = models.CharField(max_length=254)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    longitude = models.DecimalField(max_digits=9, decimal_places=6, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    created = models.DateField(auto_now_add=True)
    user = models.ForeignKey('users.User', models.PROTECT)
    type = models.CharField(choices=TYPES_CHOICES, max_length=255)  # This field type is a guess.
    picture = models.ImageField(upload_to="etablissement", blank=True)

    class Meta:
        managed = False
        db_table = 'etablissement'

    def __str__(self):
        return self.name




class Hotel(RawModel):
    etablissement = models.OneToOneField(Etablissement, models.CASCADE, primary_key=True)
    stars = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    rooms = models.IntegerField(validators=[MinValueValidator(0)])
    price = models.IntegerField(validators=[MinValueValidator(0)])

    class Meta:
        managed = False
        db_table = 'hotel'

    def __str__(self):
        return self.etablissement.name



class Restaurant(RawModel):
    etablissement = models.OneToOneField(Etablissement, models.CASCADE, primary_key=True)
    price_range = models.IntegerField(validators=[MinValueValidator(0)])
    max_seats = models.IntegerField(validators=[MinValueValidator(0)])
    takeaway = models.BooleanField()
    delivery = models.BooleanField()
    openings = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'restaurant'

    def __str__(self):
        return self.etablissement.name


class Bar(RawModel):
    etablissement = models.OneToOneField(Etablissement, models.CASCADE, primary_key=True)
    smoker = models.BooleanField()
    food = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'bar'

    def __str__(self):
        return self.etablissement.name
