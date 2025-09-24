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
        context['visits'] = Visit.objects.filter(restaurant=self.object).order_by('-date')
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = VisitForm(request.POST, request.FILES)
        
        if form.is_valid():
            visit = form.save(commit=False)
            visit.restaurant = self.object
            visit.save()

            images = request.FILES.getlist('images')
            print("画像枚数:", len(images))
            
            for image in images:
                VisitImage.objects.create(visit=visit, image=image)
                print("保存した画像:", image)  # ← デバッグ2

            return redirect('restaurants:restaurant_detail', pk=self.object.pk)
        else:
            print(form.errors)
            
            context = self.get_context_data(form=form)
            return self.render_to_response(context)