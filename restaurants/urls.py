from django.urls import path
from .views import RestaurantCreateView, RestaurantListView, RestaurantDetailView, VisitCreateView


app_name = "restaurants"

urlpatterns = [
    path("add/", RestaurantCreateView.as_view(), name="restaurant_add"),
    path("", RestaurantListView.as_view(), name="restaurant_list"),
    path("<int:pk>/", RestaurantDetailView.as_view(), name="restaurant_detail"),
    path("<int:restaurant_id>/visit/add/", VisitCreateView.as_view(), name="visit_add"),
]

