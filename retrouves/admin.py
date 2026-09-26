from django.contrib import admin
from .models import TypeDocument, PosteDePolice, Document, ProfilAgent
from django.utils import timezone

admin.site.register(ProfilAgent)
# Register your models here.
from .models import TypeDocument, PosteDePolice, Document
admin.site.register(TypeDocument)
admin.site.register(PosteDePolice)
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["code_reference", "nom_proprietaire", "type", "date_decouverte", "poste", "statut"]
    list_filter = ["statut", "type", "poste"]
    search_fields = ["nom_proprietaire"]
    readonly_fields = ["code_reference"]
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        profil = getattr(request.user, "profilagent", None)
        if profil is None:
            return qs.none()
        return qs.filter(poste=profil.poste)
    actions = ["marquer_recupere"]
    readonly_fields = ["date_recuperation", "agent_recuperation"]

    @admin.action(description="Marquer comme récupéré (après vérification d'identité)")
    def marquer_recupere(self, request, queryset):
        n = queryset.filter(statut="depose").update(
            statut="recupere",
            date_recuperation=timezone.now(),
            agent_recuperation=request.user,
        )
        self.message_user(request, f"{n} document(s) marqué(s) comme récupéré(s).")