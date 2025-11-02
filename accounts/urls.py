from django.urls import path
from .views import SignUpView, CustomLoginView, HomeView, CustomLogoutView, mypage, EmailChangeView, PasswordChangeViewWithModal
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordChangeForm

app_name = "accounts"

urlpatterns = [
    path('signup/', SignUpView.as_view(), name="signup"),
    path('login/', CustomLoginView.as_view(), name="login"),
    path('home/', HomeView.as_view(), name="home"),
    path('logout/', CustomLogoutView.as_view(), name="logout"),
    path("mypage/", mypage, name="mypage"),
    path('email/change/', EmailChangeView.as_view(), name='email_change'),
    path('password/change/', PasswordChangeViewWithModal.as_view(), name='password_change'),
]
