"""mid URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from main.views import *
from account.views import ProfileDetailViewSet
from mid import settings


router = SimpleRouter()
router.register('categories', CategoryViewSet)
router.register('posts', PostViewSet)
router.register('images', PostImageViewSet)
router.register('favorite', FavoriteView)
router.register('profile', ProfileDetailViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title='My API',
        default_version='v1',
        description='My ecommerce API'
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('account.urls')),
    path('api/v1/', include(router.urls)),
    path('api/v1/docs/', schema_view.with_ui('swagger'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
