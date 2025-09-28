from django.urls import path
from . import views
from .views import RestaurantCreateView, RestaurantDetailView, RestaurantSearchView, WantRestaurantListView, WentRestaurantListView, RestaurantListView, TagCreateView


app_name = "restaurants"

urlpatterns = [
    path("add/", RestaurantCreateView.as_view(), name="restaurant_add"),
    path("want/", views.WantRestaurantListView.as_view(), name="restaurant_list_want"),
    path("went/", views.WentRestaurantListView.as_view(), name="restaurant_list_went"),
    path("<int:pk>/", RestaurantDetailView.as_view(), name="restaurant_detail"),
    path("search/", RestaurantSearchView.as_view(), name="restaurant_search"),
    path('', RestaurantListView.as_view(), name='restaurant_list'),
    path('tags/add/', TagCreateView.as_view(), name='tag_add'),
]

