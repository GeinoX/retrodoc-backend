from django.contrib import admin

# Register your models here.
from .models import TypeDocument, PosteDePolice, Document
admin.site.register(TypeDocument)
admin.site.register(PosteDePolice)
admin.site.register(Document)