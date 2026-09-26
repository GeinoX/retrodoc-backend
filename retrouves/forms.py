from django import forms
from .models import Document

class DeclarationForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["type", "nom_proprietaire", "date_naissance", "numero_document", "date_decouverte", "lieu_decouverte", "poste", "contact_declarant"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["poste"].label_from_instance = lambda p: p.departement 