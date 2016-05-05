from django.shortcuts import render
from etablissements.models import Etablissement

def list_etablissements(request):
    context = {"bars" : [Etablissement(name="Bastoche"), Etablissement(name="Tavernier")]}
    return render(request, "etablissements_list.html", context)
