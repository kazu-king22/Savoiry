from django.views import View
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .models import Restaurant, Visit, VisitImage, Tag
from .forms import RestaurantForm, VisitForm


class RestaurantCreateView(LoginRequiredMixin, CreateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "restaurants/restaurant_form.html"
    success_url = reverse_lazy("restaurants:restaurant_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


# 気になるビュー
class WantRestaurantListView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = "restaurants/restaurant_list_want.html"
    context_object_name = "restaurants"

    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user, status="want").order_by("-created_at")

# 行ったビュー
class WentRestaurantListView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = "restaurants/restaurant_list_went.html"
    context_object_name = "restaurants"

    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user, status="went").order_by("-created_at")



class RestaurantDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        form = VisitForm()
        visits = Visit.objects.filter(restaurant=restaurant).order_by('-date')
        return render(request, "restaurants/restaurant_detail.html", {
            "restaurant": restaurant,
            "form": form,
            "visits": visits,
        })

    def post(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        form = VisitForm(request.POST, request.FILES)

        if form.is_valid():
            visit = form.save(commit=False)
            visit.restaurant = restaurant
            visit.save()

            images = request.FILES.getlist('images')
            for image in images:
                VisitImage.objects.create(visit=visit, image=image)
                
            if restaurant.status == 'want':
                restaurant.status = 'went'
                restaurant.save()

            return redirect("restaurants:restaurant_detail", pk=restaurant.pk)
        else:
            visits = Visit.objects.filter(restaurant=restaurant).order_by('-date')
            return render(request, "restaurants/restaurant_detail.html", {
                "restaurant": restaurant,
                "form": form,
                "visits": visits,
            })


class RestaurantSearchView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = "restaurants/restaurant_search.html"
    context_object_name = "restaurants"

    def get_queryset(self):
        queryset = Restaurant.objects.filter(user=self.request.user).order_by("-created_at")

        # ステータス（want / went）
        status = self.request.GET.get("status")
        if status == "want":
            queryset = queryset.filter(status="want")
        elif status == "went":
            queryset = queryset.filter(status="went")

        # 検索条件の取得
        genre = self.request.GET.get("genre")
        area = self.request.GET.get("area")
        companions = self.request.GET.get("companions")
        scene = self.request.GET.get("scene")
        closed_day = self.request.GET.get("closed_day")
        tag = self.request.GET.get("tag")

        # ✅ 必須：genreとareaが入力されてないと結果を返さない
        if not genre or not area:
            return queryset.none()

        # 🔍 フィルター条件
        queryset = queryset.filter(genre__icontains=genre, area__icontains=area)
        if companions:
            queryset = queryset.filter(companions__icontains=companions)
        if scene:
            queryset = queryset.filter(scene__icontains=scene)
        if closed_day:
            queryset = queryset.filter(closed_day__icontains=closed_day)
        if tag:
            queryset = queryset.filter(tags__name__icontains=tag)

        return queryset
    

class RestaurantListView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = "restaurants/restaurant_list.html"
    context_object_name = "restaurants"

    def get_queryset(self):
        queryset = Restaurant.objects.filter(user=self.request.user).order_by("-created_at")

        # タグ絞り込み
        tag = self.request.GET.get("tag")
        if tag:
            queryset = queryset.filter(tags__name=tag)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()  # タグ一覧をテンプレートに送る
        return context


class TagCreateView(LoginRequiredMixin, CreateView):
    model = Tag
    fields = ['name', 'category']  
    template_name = 'restaurants/restaurant_tag_form.html'
    success_url = reverse_lazy('restaurants:restaurant_list')