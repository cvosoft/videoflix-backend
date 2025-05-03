"""
URL configuration for videoflix project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls
from .views import PublicConfirmEmailView


urlpatterns = [
    path('admin/', admin.site.urls),
    # login/logout/password reset etc.
    path('api/', include('dj_rest_auth.urls')),
    # Registrierung
    path('api/registration/', include('dj_rest_auth.registration.urls')),
    #path('api/account/', include('allauth.account.urls')),
    path('api/confirm-email/', PublicConfirmEmailView.as_view()),
] + debug_toolbar_urls()

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
