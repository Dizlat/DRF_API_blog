from django.urls import path

from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('activate/', ActivationView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('forgot/', ForgotPasswordView.as_view())
    # path('profile/', ProfileView.as_view())
]