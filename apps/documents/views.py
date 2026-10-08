from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated

from .models import DocumentCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = [
            "id",
            "code",
            "name_en",
            "name_fr",
            "display_order",
            "is_active",
        ]


class CategoryList(generics.ListAPIView):
    queryset = DocumentCategory.objects.filter(
        is_active=True
    )
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]