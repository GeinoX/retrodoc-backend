from django import forms
from .models import Document

class DeclarationForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["type", "nom_proprietaire", "date_naissance", "numero_document", "date_decouverte", "lieu_decouverte", "poste", "contact_declarant"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["poste"].label_from_instance = lambda p: p.departement 

class RechercheForm(forms.Form):
    nom = forms.CharField(label="Votre nom complet")
    date_naissance = forms.DateField(label="Votre date de naissance", required=False)
    numero_document = forms.CharField(label="Numéro de votre document", required=False)
    
    def clean(self):
        data = super().clean()
        if not data.get("date_naissance") and not data.get("numero_document"):
            raise forms.ValidationError(
                "Indiquez aussi votre date de naissance ou le numéro de votre document."
            )
        return data