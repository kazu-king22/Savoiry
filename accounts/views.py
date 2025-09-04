from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import SignUpForm, EmailLoginForm
from .models import User


class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy('accounts:login')  


class CustomLoginView(LoginView):
    form_class = EmailLoginForm
    template_name = "accounts/login.html"


class CustomLogoutView(LogoutView):
    template_name = "accounts/logout.html"


class HomeView(TemplateView):
    template_name = "accounts/home.html"
