"""
URL configuration for edu_insight_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from rest_framework.routers import DefaultRouter

# PASTIKAN BARIS INI BENAR-BENAR ADA DAN TIDAK ADA DUPLIKASI ATAU TYPO
from edu_core.views import SchoolViewSet, StudentViewSet, SchoolAnalyticsView

router = DefaultRouter()
router.register(r'schools', SchoolViewSet)
router.register(r'students', StudentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # PASTIKAN BARIS INI JUGA ADA DAN TIDAK ADA TYPO
    path('api/school-analytics/', SchoolAnalyticsView.as_view(), name='school-analytics'),
]
