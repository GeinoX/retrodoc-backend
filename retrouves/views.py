from django.shortcuts import redirect, render
from .forms import DeclarationForm
from django.shortcuts import get_object_or_404, redirect, render
from .models import Document
from django.db.models import Q
from .forms import DeclarationForm, RechercheForm

# Create your views here.
def accueil(request):
    return render(request, "retrouves/accueil.html")

def declarer (request):
    form = DeclarationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        doc = form.save()
        return redirect("merci", code=doc.code_reference)
    return render(request, "retrouves/declarer.html", {"form": form})

def merci(request, code):
    doc = get_object_or_404(Document, code_reference=code)
    return render(request, "retrouves/merci.html", {"doc": doc})

def rechercher(request):
    form = RechercheForm(request.POST or None)
    resultats = None
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        criteres = Q(nom_proprietaire__iexact=d["nom"]) & Q(statut="depose")
        if d["date_naissance"]:
            criteres &= Q(date_naissance=d["date_naissance"])
        if d["numero_document"]:
            criteres &= Q(numero_document__iexact=d["numero_document"])
        resultats = Document.objects.filter(criteres)
    return render(request, "retrouves/rechercher.html", {"form": form, "resultats": resultats})