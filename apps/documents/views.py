from django.shortcuts import render
from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated

from .models import DocumentCategory

# Create your views here.

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ["id", "code", "name_en", "name_fr"]


class CategoryList(generics.ListAPIView):
    queryset = DocumentCategory.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]