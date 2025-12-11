"""
URL configuration for joblink_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from pwa.views import manifest, service_worker
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_control
from core import views_admin  # ou l’app qui contient ta vue




urlpatterns = [
    # ... tes autres URLs ...
    path(
    'admin/core/abonnement/<int:abonnement_id>/renouveler/',
    views_admin.renouveler_abonnement_admin,
    name='renouveler_abonnement_admin'
),

    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')), 
    path('', include('pwa.urls')), # pour login/logout
    path('manifest.json', manifest, name='manifest'),
    path('serviceworker.js', service_worker, name='serviceworker'),
    path(
        ".well-known/assetlinks.json",
        cache_control(no_cache=True, must_revalidate=True)(
            TemplateView.as_view(
                template_name="assetlinks.json",
                content_type="application/json"
            )
        ),
        name="assetlinks"
    ),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

