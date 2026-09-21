from django.db import models

# Create your models here.
class TypeDocument(models.Model):
    libelle = models.CharField(max_length=80, unique=True)

    def _str_(self):
        return self.libelle 

class PosteDePolice(models.Model):
    departement = models.CharField(max_length=80, unique=True)
    nom = models.CharField(max_length=120)
    adresse = models.CharField(max_length=200)
    ville = models.CharField(max_length=80)
    telephone = models.CharField(max_length=30, blank=True)

    def _str_(self):
        return f"{self.nom} ({self.departement})"

class Document(models.Model):
    STATUTS = [
        ("depose", "Déposé au poste"),
        ("recupere", "Récupéré"),
    ]

    type = models.ForeignKey(TypeDocument, on_delete=models.PROTECT)
    poste = models.ForeignKey(PosteDePolice, on_delete=models.PROTECT)
    nom_proprietaire = models.CharField(max_length=150)
    date_naissance = models.DateField(null=True, blank=True)
    numero_document = models.CharField(max_length=50, blank=True)
    date_decouverte = models.DateField()
    lieu_decouverte = models.CharField(max_length=200)
    contact_declarant = models.CharField(max_length=100, blank=True)
    statut = models.CharField(max_length=10, choices=STATUTS, default="depose")
    date_enregistrement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.nom_proprietaire}"

