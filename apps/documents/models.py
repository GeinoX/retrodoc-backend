from django.db import models

# Create your models here.

class DocumentCategory(models.Model):
    code = models.SlugField(max_length=50, unique=True)
    name_en = models.CharField(max_length=100)
    name_fr = models.CharField(max_length=100)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]
        verbose_name_plural = "document categories"

    def __str__(self):
        return self.name_en