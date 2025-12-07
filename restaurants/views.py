from django.views import View
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .models import Restaurant, Visit, VisitImage, Tag, SuggestWord
from .forms import RestaurantForm, VisitForm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "MS Gothic"
from django.http import HttpResponse, JsonResponse 
import io
from django.db.models.functions import TruncMonth
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import matplotlib
from django.http import HttpResponseForbidden
import datetime

matplotlib.rcParams['font.family'] = ['Noto Sans CJK JP', 'IPAexGothic', 'TakaoGothic', 'Meiryo', 'sans-serif']


class RestaurantCreateView(LoginRequiredMixin, CreateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "restaurants/restaurant_form.html"
    success_url = reverse_lazy("restaurants:restaurant_search")

    # ★ サジェスト候補
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["area_list"] = SuggestWord.objects.filter(word_type="area").values_list("word", flat=True)
        context["genre_list"] = SuggestWord.objects.filter(word_type="genre").values_list("word", flat=True)
        context["group_list"] = SuggestWord.objects.filter(word_type="group").values_list("word", flat=True)
        context["scene_list"] = SuggestWord.objects.filter(word_type="scene").values_list("word", flat=True)
        context["tag_list"] = SuggestWord.objects.filter(word_type="tag").values_list("word", flat=True)

        return context

    def form_valid(self, form):
       
        restaurant = form.save(commit=False)

        # 必須情報セット
        restaurant.user = self.request.user
        restaurant.status = "want"

        # -----------------------------
        # ★ 休業日の複数選択を文字列に変換して保存
        # -----------------------------
        holidays = self.request.POST.getlist("holiday")
        restaurant.holiday = ",".join(holidays)

        restaurant.save()

        # ManyToMany の tags は save_m2m() が必要
        form.save_m2m()

        # -----------------------------
        # ★ サジェスト保存処理
        # -----------------------------
        def save_suggest(word_type, value):
            if value:
                value = value.strip()
                if value:
                    SuggestWord.objects.get_or_create(
                        word_type=word_type,
                        word=value
                    )

        # 固定項目
        save_suggest("area", restaurant.area)
        save_suggest("genre", restaurant.genre)
        save_suggest("group", restaurant.companions)
        save_suggest("scene", restaurant.scene)

        # タグ保存
        tags_input = self.request.POST.getlist("tags")
        if tags_input:
            for tag_name in tags_input:
                tag_name = tag_name.strip()
                if not tag_name:
                    continue

                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                restaurant.tags.add(tag_obj)
                save_suggest("tag", tag_name)

        messages.success(self.request, "restaurant_added")

        # -----------------------------
        # ★ 最後にリダイレクト
        # -----------------------------
        return redirect("restaurants:restaurant_list_want")


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

            # ★ 画像を取得（ここが最重要）
            images = request.FILES.getlist("images")

            # ★ 5枚を超えていたらエラーを出して return
            if len(images) > 5:
                messages.error(request, "写真は1回の訪問につき最大5枚まで登録できます。")

                visits = Visit.objects.filter(restaurant=restaurant).order_by('-date')
                return render(request, "restaurants/restaurant_detail.html", {
                    "restaurant": restaurant,
                    "form": form,
                    "visits": visits,
                })

            # ★ 枚数OKなら Visit 保存
            visit = form.save(commit=False)
            visit.restaurant = restaurant

            if not visit.date:
                visit.date = timezone.now().date()

            visit.save()

            # ★ 画像の保存処理
            for image in images:
                VisitImage.objects.create(visit=visit, image=image)

            # ステータス更新
            if restaurant.status == 'want':
                restaurant.status = 'went'
                restaurant.save()

            messages.success(request, "went_added")
            return redirect("restaurants:restaurant_list_went")

        # フォームエラー時
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

        if self.request.session.pop("just_signed_up", False):
            messages.success(self.request, "login_first")

        context["want_count"] = Restaurant.objects.filter(user=user, status="want").count()
        context["went_count"] = Restaurant.objects.filter(user=user, status="went").count()

        context["area_list"] = SuggestWord.objects.filter(word_type="area").values_list("word", flat=True)
        context["genre_list"] = SuggestWord.objects.filter(word_type="genre").values_list("word", flat=True)
        context["group_list"] = SuggestWord.objects.filter(word_type="group").values_list("word", flat=True)
        context["scene_list"] = SuggestWord.objects.filter(word_type="scene").values_list("word", flat=True)
        context["tag_list"] = SuggestWord.objects.filter(word_type="tag").values_list("word", flat=True)

        # ★ 休業日の選択肢（検索画面用）
        context["holiday_choices"] = Restaurant.DAY_CHOICES

        # ★ 検索時の選択済みの休業日（編集 UI の初期値用）
        context["selected_holidays"] = self.request.GET.getlist("holiday")

        return context


class RestaurantSearchResultView(LoginRequiredMixin, ListView):
    model = Restaurant
    context_object_name = "restaurants"

    def get_queryset(self):
        queryset = Restaurant.objects.filter(user=self.request.user).order_by("-created_at")

        genre = self.request.GET.get("genre")
        area = self.request.GET.get("area")
        companions = self.request.GET.get("companions")
        scene = self.request.GET.get("scene")
        holidays = self.request.GET.getlist("holiday")
        tag = self.request.GET.get("tag")
        status = self.request.GET.get("status")  # ← 追加フィルター対象

        # ---- 個別フィルター ----
        if genre:
            queryset = queryset.filter(genre__icontains=genre)
        if area:
            queryset = queryset.filter(area__icontains=area)
        if companions:
            queryset = queryset.filter(companions__icontains=companions)
        if scene:
            queryset = queryset.filter(scene__icontains=scene)
        if holidays:
            q_obj = Q()
            for h in holidays:
                q_obj |= Q(holiday__icontains=h)
            queryset = queryset.filter(q_obj)
        if tag:
            queryset = queryset.filter(tags__name__icontains=tag)

        # ---- ★ステータスフィルター（改善版）----
        if status == "want":
            queryset = queryset.filter(status="want")
        elif status == "went":
            queryset = queryset.filter(status="went")
        elif status == "all":
            pass
        else:
            # 初期状態は「絞り込みなし」
            pass

        return queryset

    def get_template_names(self):
        """status値に応じてテンプレートを切り替える"""
        status = self.request.GET.get("status")

        if status == "want":
            return ["restaurants/restaurant_search_result_want.html"]
        elif status == "went":  
            return ["restaurants/restaurant_search_result_went.html"]
        elif status == "all":
            return ["restaurants/restaurant_search_result_all.html"]

        # 初期状態も全体
        return ["restaurants/restaurant_search_result_all.html"]




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


class VisitUpdateView(LoginRequiredMixin, UpdateView):
    model = Visit
    form_class = VisitForm
    template_name = "restaurants/restaurant_visit_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["original_visit"] = self.object
        context["restaurant"] = self.object.restaurant
        context["is_edit"] = True
        return context

    def form_valid(self, form):

        visit = self.object  # 編集対象の Visit
    
    # ===== 未来日チェック =====
        visit_date = form.cleaned_data.get("date")

        if isinstance(visit_date, str):
            try:
                visit_date = datetime.datetime.strptime(visit_date, "%Y-%m-%d").date()
            except:
                pass

        today = timezone.localdate()

        if visit_date and visit_date > today:
            form.add_error("date", "未来日は登録できません。")
            return self.form_invalid(form)

    # ===== 画像チェック =====
        existing_count = visit.images.count()
        new_images = self.request.FILES.getlist('images')
        new_count = len(new_images)

        if existing_count + new_count > 5:
            messages.error(self.request, "写真は1回の訪問につき最大5枚まで登録できます。")
            return self.form_invalid(form)

        response = super().form_valid(form)

        for image in new_images:
            VisitImage.objects.create(visit=visit, image=image)

        return response

    def get_success_url(self):
        restaurant = self.object.restaurant
        return reverse_lazy(
            "restaurants:restaurant_detail_went",
            kwargs={"pk": restaurant.pk}
        )

class VisitRevisitStoreView(LoginRequiredMixin, View):

    def get(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk, user=request.user)
        form = VisitForm()

        return render(request, "restaurants/restaurant_visit_form.html", {
            "restaurant": restaurant,
            "form": form,
            "is_edit": False,
        })

    def post(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk, user=request.user)
        form = VisitForm(request.POST, request.FILES)

        if form.is_valid():
            images = request.FILES.getlist("images")

            # ★ ここが一番重要（5枚制限）★
            if len(images) > 5:
                messages.error(request, "写真は1回の訪問につき最大5枚まで登録できます。")
                return redirect(request.path)

            visit = form.save(commit=False)
            visit.restaurant = restaurant
            visit.save()

            # 画像保存
            for img in images:
                VisitImage.objects.create(visit=visit, image=img)

            return redirect("restaurants:restaurant_detail_went", pk=restaurant.pk)

        return render(request, "restaurants/restaurant_visit_form.html", {
            "restaurant": restaurant,
            "form": form,
            "is_edit": False,
        })


class TagCreateView(LoginRequiredMixin, CreateView):
    model = Tag
    fields = ['name', 'category']
    template_name = 'restaurants/restaurant_tag_form.html'
    success_url = reverse_lazy('restaurants:restaurant_list')


class VisitDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        visit = get_object_or_404(Visit, pk=pk)

        if visit.restaurant.user != request.user:
            return HttpResponseForbidden()

        restaurant_id = visit.restaurant.id
        visit.delete()

        messages.success(request, "訪問記録を削除しました")

        return redirect("restaurants:restaurant_detail_went", restaurant_id)


class RestaurantEditView(LoginRequiredMixin, UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "restaurants/restaurant_edit.html"

    # ★ 保存後の遷移先を分岐
    def get_success_url(self):
        if self.request.GET.get("from") == "went":
            # 行ったお店の詳細ページへ
            return reverse("restaurants:restaurant_detail_went", kwargs={"pk": self.object.pk})
        
        # 気になるの詳細ページへ
        return reverse("restaurants:restaurant_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["area_list"] = SuggestWord.objects.filter(word_type="area").values_list("word", flat=True)
        context["genre_list"] = SuggestWord.objects.filter(word_type="genre").values_list("word", flat=True)
        context["group_list"] = SuggestWord.objects.filter(word_type="group").values_list("word", flat=True)
        context["scene_list"] = SuggestWord.objects.filter(word_type="scene").values_list("word", flat=True)
        context["tag_list"] = SuggestWord.objects.filter(word_type="tag").values_list("word", flat=True)

        # タグ（編集時）
        restaurant = self.object
        context["selected_tags"] = restaurant.tags.values_list("name", flat=True)
        return context

    def form_valid(self, form):
        # ▼ 休業日の複数選択を保存
        holidays = self.request.POST.getlist("holiday")
        form.instance.holiday = "、".join(holidays)

        response = super().form_valid(form)

        # ▼ タグ更新処理
        restaurant = self.object
        tags = self.request.POST.getlist("tags")
        tags = [t.strip() for t in tags if t.strip()]
        restaurant.tags.clear()

        from .models import Tag
        for tagname in tags:
            tag_obj, created = Tag.objects.get_or_create(name=tagname)
            restaurant.tags.add(tag_obj)

        return response


def visit_chart_monthly(request):
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse
    from django.db.models.functions import TruncMonth
    from django.db.models import Count

    plt.close("all")

    if not request.user.is_authenticated:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "ログインが必要です", fontsize=40, ha="center", va="center")
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
        ax.text(0.5, 0.5, "データがありません", fontsize=20, ha="center", va="center")
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

    ax.set_title("月別訪問数", fontsize=30, fontweight="bold")

    ax.tick_params(axis='x', labelsize=30, width=1.2)
    ax.tick_params(axis='y', labelsize=30, width=1.2)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(months, fontsize=30, fontweight="bold")

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
            fontsize=30,
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

    if not genre_counts.exists():
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.text(
            0.5, 0.5,
            "データがありません",
            ha="center", va="center",
            fontsize=16, color="black"
            
        )
        ax.set_axis_off()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white", dpi=150)
        plt.close("all")
        buf.seek(0)
        return HttpResponse(buf.getvalue(), content_type="image/png")

    genres = [g["restaurant__genre"] or "未分類" for g in genre_counts]
    counts = [g["count"] for g in genre_counts]

    fig, ax = plt.subplots(figsize=(5, 3))
    bars = ax.barh(genres, counts, color="#4a6cf7", alpha=0.85, height=0.5)
    
    ax.set_title("")
    fig.text(0, 0.95, "ジャンル別訪問数", fontsize=19, fontweight="bold", ha="left", va="center")
    
    ax.tick_params(axis='y', labelsize=16, length=0)
    ax.tick_params(axis='x', bottom=False, labelbottom=False)
    ax.invert_yaxis()

    for i, bar in enumerate(bars):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                str(counts[i]), va='center', fontsize=20, fontweight="bold", color="#333")

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


@login_required
def delete_visit_image(request, image_id):
    image = get_object_or_404(
        VisitImage,
        id=image_id,
        visit__restaurant__user=request.user
    )

    if request.method == "POST":
        deleted_id = f"image-{image_id}"
        image.delete()
        return JsonResponse({"success": True, "deleted_id": deleted_id})

    return JsonResponse({"success": False}, status=400)



# class VisitRevisitView(View):
#     def get(self, request, pk):
#         original_visit = get_object_or_404(Visit, pk=pk)
#         form = VisitForm()
#         return render(request, "restaurants/visit_form.html", {
#             "form": form,
#             "original_visit": original_visit,
#         })

#     def post(self, request, pk):
#         original_visit = get_object_or_404(Visit, pk=pk)
#         restaurant = original_visit.restaurant
#         form = VisitForm(request.POST, request.FILES)

#         if form.is_valid():
#             new_visit = form.save(commit=False)
#             new_visit.restaurant = restaurant
#             new_visit.save()


#             images = request.FILES.getlist("images")
#             for image in images:
#                 VisitImage.objects.create(visit=new_visit, image=image)

#             return redirect("restaurants:restaurant_detail_went", pk=restaurant.pk)
#         else:
#             return render(request, "restaurants/visit_form.html", {
#                 "form": form,
#                 "original_visit": original_visit,
#             })