from django.views import View
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .models import Restaurant, Visit, VisitImage
from .forms import RestaurantForm, VisitForm


class RestaurantCreateView(LoginRequiredMixin, CreateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "restaurants/restaurant_form.html"
    success_url = reverse_lazy("restaurants:restaurant_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class RestaurantListView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = "restaurants/restaurant_list.html"
    context_object_name = "restaurants"

    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user).order_by("-created_at")


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

            return redirect("restaurants:restaurant_detail", pk=restaurant.pk)
        else:
            visits = Visit.objects.filter(restaurant=restaurant).order_by('-date')
            return render(request, "restaurants/restaurant_detail.html", {
                "restaurant": restaurant,
                "form": form,
                "visits": visits,
            })
