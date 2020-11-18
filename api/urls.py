from django.urls import path, include
from rest_framework import routers
from rest_framework.decorators import api_view
from rest_framework.response import Response

# router = routers.SimpleRouter()
# router.register('', )

@api_view(['GET'])
def api_root(request):
    response = {
        'message': 'Welcome to My Top 100 Movies.'
    }
    return Response(response)

urlpatterns = [
    path('', api_root),
    path('auth', include('rest_framework.urls')),
]