from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from cms_app.views import *

router = DefaultRouter()
router.register('user', UserViewSet, basename='user')
router.register('content', ContentViewSet, basename='content')

urlpatterns = [
    path('signup/',SignUpAPIView.as_view(), name='signup'),
    path('login/',LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += router.urls