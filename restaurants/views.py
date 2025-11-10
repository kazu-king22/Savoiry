from django.views import View
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .models import Restaurant, Visit, VisitImage, Tag
from .forms import RestaurantForm, VisitForm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "MS Gothic"
from django.http import HttpResponse
import io
from django.db.models.functions import TruncMonth
from django.db.models import Count, Avg
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import matplotlib
matplotlib.rcParams['font.family'] = ['Noto Sans CJK JP', 'IPAexGothic', 'TakaoGothic', 'Meiryo', 'sans-serif']


class RestaurantCreateView(LoginRequiredMixin, CreateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "restaurants/restaurant_form.html"
    success_url = reverse_lazy("restaurants:restaurant_search")

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = "want"

        response = super().form_valid(form)

        tags_input = self.request.POST.getlist("tags")

        if tags_input:
            for tag_name in tags_input:
                tag_name = tag_name.strip()
                if not tag_name:
                    continue
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                self.object.tags.add(tag_obj)

        messages.success(self.request, "restaurant_added")
        return redirect("restaurants:restaurant_add")


class VisitCreateView(LoginRequiredMixin, CreateView):
    model = Visit
    form_class = VisitForm
    template_name = "restaurants/visit_form.html"

    def form_valid(self, form):
        restaurant_id = self.kwargs["restaurant_id"]
        restaurant = Restaurant.objects.get(id=restaurant_id)


        form.instance.restaurant = restaurant
        response = super().form_valid(form)


        restaurant.status = "went"
        restaurant.save()

        return response

    def get_success_url(self):
        return reverse_lazy("restaurants:restaurant_detail", kwargs={"pk": self.object.restaurant.pk})




class WantRestaurantListView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = "restaurants/restaurant_list_want.html"
    context_object_name = "restaurants"

    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user, status="want").order_by("-created_at")


class WentRestaurantListView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = "restaurants/restaurant_list_went.html"
    context_object_name = "restaurants"

    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user, status="went").prefetch_related("visits").order_by("-created_at")



class RestaurantDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk, user=request.user)
        form = VisitForm()
        visits = Visit.objects.filter(restaurant=restaurant).order_by('-date')
        return render(request, "restaurants/restaurant_detail.html", {
            "restaurant": restaurant,
            "form": form,
            "visits": visits,
        })

    def post(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk, user=request.user)
        form = VisitForm(request.POST, request.FILES)

        if form.is_valid():
            visit = form.save(commit=False)
            visit.restaurant = restaurant

            if not visit.date:
                visit.date = timezone.now().date()
            visit.save()

            images = request.FILES.getlist('images')
            for image in images:
                VisitImage.objects.create(visit=visit, image=image)

            if restaurant.status == 'want':
                restaurant.status = 'went'
                restaurant.save()

            return redirect("restaurants:restaurant_list_want")


        visits = Visit.objects.filter(restaurant=restaurant).order_by('-date')
        return render(request, "restaurants/restaurant_detail.html", {
            "restaurant": restaurant,
            "form": form,
            "visits": visits,
        })


class RestaurantDeleteView(LoginRequiredMixin, DeleteView):
    model = Restaurant
    template_name = "restaurants/restaurant_confirm_delete.html"
    success_url = reverse_lazy("restaurants:restaurant_list_want")

    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user)


class RestaurantResetView(LoginRequiredMixin, View):
    def post(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk, user=request.user)

        visits = restaurant.visits.all()
        for visit in visits:
            visit.images.all().delete()
        visits.delete()

        restaurant.status = "want"
        restaurant.save()

        return redirect(reverse_lazy("restaurants:restaurant_list_want"))



class RestaurantSearchView(LoginRequiredMixin, TemplateView):
    template_name = "restaurants/restaurant_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["want_count"] = Restaurant.objects.filter(user=user, status="want").count()
        context["went_count"] = Restaurant.objects.filter(user=user, status="went").count()
        return context



class RestaurantSearchResultView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = "restaurants/restaurant_search_result.html"
    context_object_name = "restaurants"

    def get_queryset(self):
        queryset = Restaurant.objects.filter(user=self.request.user).order_by("-created_at")

        genre = self.request.GET.get("genre")
        area = self.request.GET.get("area")
        companions = self.request.GET.get("companions")
        scene = self.request.GET.get("scene")
        closed_day = self.request.GET.get("closed_day")
        tag = self.request.GET.get("tag")
        status = self.request.GET.get("status")


        if genre:
            queryset = queryset.filter(genre__icontains=genre)
        if area:
            queryset = queryset.filter(area__icontains=area)
        if companions:
            queryset = queryset.filter(companions__icontains=companions)
        if scene:
            queryset = queryset.filter(scene__icontains=scene)
        if closed_day:
            queryset = queryset.filter(closed_day__icontains=closed_day)
        if tag:
            queryset = queryset.filter(tags__name__icontains=tag)
        if status:
            queryset = queryset.filter(status=status)

        return queryset




class RestaurantListView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = "restaurants/restaurant_list.html"
    context_object_name = "restaurants"

    def get_queryset(self):
        queryset = Restaurant.objects.filter(user=self.request.user).order_by("-created_at")


        tag = self.request.GET.get("tag")
        if tag:
            queryset = queryset.filter(tags__name=tag)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        return context


class WentRestaurantDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk, user=request.user)


        visits = Visit.objects.filter(restaurant=restaurant).order_by('-date')

        return render(request, "restaurants/restaurant_detail_went.html", {
            "restaurant": restaurant,
            "visits": visits,
        })


class VisitUpdateView(UpdateView):
    model = Visit
    form_class = VisitForm
    template_name = "restaurants/visit_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["original_visit"] = self.object
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        images = self.request.FILES.getlist('images')
        for image in images:
            VisitImage.objects.create(visit=self.object, image=image)

        return response

    def get_success_url(self):
        restaurant = getattr(self.object, "restaurant", None)
        if restaurant and restaurant.pk:
            return reverse_lazy("restaurants:restaurant_detail_went", kwargs={"pk": restaurant.pk})
        else:
            return reverse_lazy("restaurants:restaurant_list_went")




class VisitRevisitView(View):
    def get(self, request, pk):
        original_visit = get_object_or_404(Visit, pk=pk)
        form = VisitForm()
        return render(request, "restaurants/visit_form.html", {
            "form": form,
            "original_visit": original_visit,
        })

    def post(self, request, pk):
        original_visit = get_object_or_404(Visit, pk=pk)
        restaurant = original_visit.restaurant
        form = VisitForm(request.POST, request.FILES)

        if form.is_valid():
            new_visit = form.save(commit=False)
            new_visit.restaurant = restaurant
            new_visit.save()


            images = request.FILES.getlist("images")
            for image in images:
                VisitImage.objects.create(visit=new_visit, image=image)

            return redirect("restaurants:restaurant_detail_went", pk=restaurant.pk)
        else:
            return render(request, "restaurants/visit_form.html", {
                "form": form,
                "original_visit": original_visit,
            })


class TagCreateView(LoginRequiredMixin, CreateView):
    model = Tag
    fields = ['name', 'category']
    template_name = 'restaurants/restaurant_tag_form.html'
    success_url = reverse_lazy('restaurants:restaurant_list')


def visit_chart_monthly(request):
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse
    from django.db.models.functions import TruncMonth
    from django.db.models import Count

    plt.close("all")

    if not request.user.is_authenticated:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "ログインが必要です", fontsize=14, ha="center", va="center")
        ax.axis("off")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
        plt.close("all")
        buf.seek(0)
        return HttpResponse(buf.getvalue(), content_type="image/png")

    visits_by_month = (
        Visit.objects
        .filter(restaurant__user=request.user)
        .annotate(month=TruncMonth("date"))
        .exclude(month=None)
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    if not visits_by_month:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "データがありません", fontsize=14, ha="center", va="center")
        ax.axis("off")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
        plt.close("all")
        buf.seek(0)
        return HttpResponse(buf.getvalue(), content_type="image/png")

    months = [f"{v['month'].month}月" for v in visits_by_month]
    counts = [v["count"] for v in visits_by_month]

    fig, ax = plt.subplots(figsize=(9, 4))
    x_positions = range(len(months))
    bars = ax.bar(x_positions, counts, color="#5a8dee", width=0.6)

    ax.set_title("月別訪問数", fontsize=16, fontweight="bold")

    ax.tick_params(axis='x', labelsize=16, width=1.2)
    ax.tick_params(axis='y', labelsize=16, width=1.2)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(months, fontsize=14, fontweight="bold")

    ax.set_ylim(0, 20)
    ax.set_yticks(range(0, 21, 5))

    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.4,
            f"{int(height)}",
            ha="center",
            va="bottom",
            fontsize=16,
            fontweight="bold",
            color="#333"
        )

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
    plt.close("all")
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type="image/png")



def visit_chart_top3_genre(request):
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse
    from django.db.models import Count

    plt.close("all")

    visits_by_genre = (
        Visit.objects
        .filter(restaurant__user=request.user)
        .values("restaurant__genre")
        .annotate(count=Count("id"))
        .order_by("-count")[:3]
    )

    genres = [v["restaurant__genre"] or "未分類" for v in visits_by_genre]
    counts = [v["count"] for v in visits_by_genre]

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(genres, counts, color="orange")
    for i, v in enumerate(counts):
        ax.text(i, v + 0.2, str(v), ha="center")

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
    plt.close("all")
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type="image/png")


def visit_chart_genre(request):
    from django.db.models import Count
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse

    plt.close("all")

    genre_counts = (
        Visit.objects.filter(restaurant__user=request.user)
        .values("restaurant__genre")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    genres = [g["restaurant__genre"] or "未分類" for g in genre_counts]
    counts = [g["count"] for g in genre_counts]

    fig, ax = plt.subplots(figsize=(5, 3))
    bars = ax.barh(genres, counts, color="#4a6cf7", alpha=0.85, height=0.5)


    ax.set_title("")
    fig.text(0, 0.95, "ジャンル別訪問数", fontsize=14, fontweight="bold", ha="left", va="center")

    ax.tick_params(axis='y', labelsize=12, length=0)
    ax.tick_params(axis='x', bottom=False, labelbottom=False)
    ax.invert_yaxis()

    for i, bar in enumerate(bars):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                str(counts[i]), va='center', fontsize=12, fontweight="bold", color="#333")

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.subplots_adjust(left=0.2, right=0.95, top=0.9, bottom=0.1)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white", dpi=150)
    plt.close("all")
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type="image/png")