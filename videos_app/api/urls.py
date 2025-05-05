# urls.py (DRF Router)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SerieViewSet, PredigtViewSet

router = DefaultRouter()
router.register(r'serien', SerieViewSet, basename='serien')
router.register(r'predigten', PredigtViewSet, basename='predigten')


urlpatterns = [
    path('', include(router.urls)),
]
