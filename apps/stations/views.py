from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated

from .models import Region, Station


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = [
            "id",
            "name_en",
            "name_fr",
        ]


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = [
            "id",
            "name",
            "region",
            "address",
            "phone",
            "opening_hours",
            "is_active",
        ]


class RegionList(generics.ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticated]


class StationList(generics.ListAPIView):
    serializer_class = StationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        stations = Station.objects.filter(
            is_active=True
        )

        region = self.request.query_params.get("region")

        if region:
            return stations.filter(
                region_id=region
            )

        return stations