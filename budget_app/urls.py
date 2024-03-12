"""finance_by_month URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.views.static import serve
from django.urls import path, re_path
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

from app.views import HomeView, EditFormView, EditFormActionView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('edit-form', EditFormView.as_view(), name='edit-form'),
    path('edit-form/<object_id>/<object_type>', EditFormView.as_view(), name='edit-form'),
    path('edit-form-action', EditFormActionView.as_view(), name='edit-form-action'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
