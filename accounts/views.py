from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SignUpForm, EmailLoginForm, EmailChangeForm, CustomPasswordChangeForm
from .models import User
from django.contrib.auth.decorators import login_required
from restaurants.models import Visit
from django.db.models import Avg
from django.shortcuts import render
from django.views.generic import UpdateView, View
from django.contrib import messages, auth
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.shortcuts import redirect

User = get_user_model()


class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("restaurants:restaurant_search")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        auth.login(self.request, user)

        self.request.session["just_signed_up"] = True

        return redirect("restaurants:restaurant_search")

    def form_invalid(self, form):
        messages.error(self.request, "アカウント登録に失敗しました。")
        return super().form_invalid(form)

class CustomLoginView(LoginView):
    form_class = EmailLoginForm
    template_name = "accounts/login.html"

    def get_success_url(self):
        messages.success(self.request, "ログインしました。")
        return reverse_lazy("restaurants:restaurant_search")

class CustomLogoutView(LogoutView):
    template_name = "accounts/logout.html"


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/home.html"

    
@login_required
def mypage(request):
    top3_visits = (
        Visit.objects
        .filter(restaurant__user=request.user, rating__isnull=False)
        .values("restaurant__store_name", "restaurant__genre")
        .annotate(avg_rating=Avg("rating"))
        .order_by("-avg_rating")[:3]
    )

    return render(request, "accounts/mypage.html", {"top3_visits": top3_visits})


class EmailChangeView(LoginRequiredMixin, View):
    template_name = "accounts/change_email.html"

    def get(self, request):
        form = EmailChangeForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = EmailChangeForm(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data["email"]
            request.user.email = new_email
            request.user.save()

            messages.success(request, "email_changed")
            return redirect("accounts:mypage")

        messages.error(request, "メールアドレス変更に失敗しました")
        return render(request, self.template_name, {"form": form})


class PasswordChangeViewWithModal(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = "accounts/password_change.html"

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "password_changed")
        return redirect("accounts:mypage")

    def form_invalid(self, form):
        messages.error(self.request, "パスワード変更に失敗しました")
        return self.render_to_response(self.get_context_data(form=form))