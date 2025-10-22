from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SignUpForm, EmailLoginForm
from .models import User
from django.contrib.auth.decorators import login_required


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


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/home.html"


class MyPageView(TemplateView):
    template_name = "accounts/mypage.html"
    
    
@login_required
def mypage(request):
    visits = Visit.objects.all()
    print("===== DEBUG =====")
    for v in visits:
        print(
            f"店舗: {v.restaurant.store_name}, "
            f"登録ユーザー: {v.restaurant.user}, "
            f"ログイン中ユーザー: {request.user}, "
            f"評価: {v.rating}"
        )

    top3_visits = (
        Visit.objects
        .filter(restaurant__user=request.user, rating__isnull=False)
        .values("restaurant__store_name", "restaurant__genre")
        .annotate(avg_rating=Avg("rating"))
        .order_by("-avg_rating")[:3]
    )

    print("==== 集計結果 ====")
    print(list(top3_visits))

    return render(request, "restaurants/mypage.html", {"top3_visits": top3_visits})
