from django.views.generic import CreateView, ListView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Restaurant, Visit, VisitImage
from .forms import RestaurantForm, VisitForm
from django.shortcuts import redirect

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


class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = "restaurants/restaurant_detail.html"
    context_object_name = "restaurant"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = VisitForm()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = VisitForm(request.POST, request.FILES)
        
        if form.is_valid():
            visit = form.save(commit=False)
            visit.restaurant = self.object
            visit.save()

            images = request.FILES.getlist('images')
            for image in images:
                VisitImage.objects.create(visit=visit, image=image)

            return redirect('restaurants:restaurant_detail', pk=self.object.pk)
        
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class VisitCreateView(CreateView):
    model = Visit
    form_class = VisitForm
    template_name = "restaurants/visit_form.html"

    def form_valid(self, form):
        restaurant_id = self.kwargs["restaurant_id"]
        restaurant = Restaurant.objects.get(pk=restaurant_id)
        form.instance.restaurant = restaurant 
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy("restaurants:restaurant_detail", kwargs={"pk": self.object.restaurant.pk})
