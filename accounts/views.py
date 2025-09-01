from django.shortcuts import render
from django.views.generic import TemplateView,CreateView
from django.http.response import HttpResponseRedirect
from django.contrib.auth import login
from django.urls import reverse_lazy
from .forms import SignUpForm, EmailLoginForm
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView

class IndexView(TemplateView):
    template_name = "accounts/index.html"

class HomeView(TemplateView):
    template_name = "accounts/home.html"

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.object = user
        return HttpResponseRedirect(self.get_success_url())

class LoginView(BaseLoginView):
    form_class = EmailLoginForm
    template_name = "accounts/login.html"

    
class LogoutView(BaseLogoutView):
    success_url = reverse_lazy("accounts:index")