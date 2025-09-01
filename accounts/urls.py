from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path('top/', views.IndexView.as_view(), name='index'),
    path('signup/', views.SignUpView.as_view(), name="signup"),
    path('home/', views.HomeView.as_view(), name="home"),
    path('login/', views.LoginView.as_view(), name="login"),
]
