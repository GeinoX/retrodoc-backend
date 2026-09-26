from django.shortcuts import redirect, render
from .forms import DeclarationForm
from django.shortcuts import get_object_or_404, redirect, render
from .models import Document

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