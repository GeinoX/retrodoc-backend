from django.db import models

# Create your models here.

class Region(models.Model):
    name_en = models.CharField(max_length=100, unique=True)
    name_fr = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name_en"]

    def __str__(self):
        return self.name_en


class Station(models.Model):
    name = models.CharField(max_length=200)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="stations")
    address = models.CharField(max_length=300)
    phone = models.CharField(max_length=30, blank=True)
    opening_hours = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["region", "name"], name="unique_station_per_region")
        ]

    def __str__(self):
        return self.name