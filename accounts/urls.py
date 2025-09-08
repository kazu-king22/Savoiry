from django.urls import path
from .views import SignUpView, CustomLoginView, HomeView, CustomLogoutView

app_name = "accounts"

urlpatterns = [
    path('signup/', SignUpView.as_view(), name="signup"),
    path('login/', CustomLoginView.as_view(), name="login"),
    path('home/', HomeView.as_view(), name="home"),
    path('logout/', CustomLogoutView.as_view(), name="logout"),
]
