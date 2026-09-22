from django.contrib import admin
from .models import TypeDocument, PosteDePolice, Document, ProfilAgent

admin.site.register(ProfilAgent)
# Register your models here.
from .models import TypeDocument, PosteDePolice, Document
admin.site.register(TypeDocument)
admin.site.register(PosteDePolice)
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["nom_proprietaire", "type", "date_decouverte", "poste", "statut"]
    list_filter = ["statut", "type", "poste"]
    search_fields = ["nom_proprietaire"]
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        profil = getattr(request.user, "profilagent", None)
        if profil is None:
            return qs.none()
        return qs.filter(poste=profil.poste)