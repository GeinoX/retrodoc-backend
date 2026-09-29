from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def test_connexion(request):
    return Response({"message": "Connexion réussie avec le backend Django"})
