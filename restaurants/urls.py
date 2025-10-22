from django.urls import path
from . import views
from .views import (
    RestaurantCreateView, 
    RestaurantDetailView, 
    RestaurantSearchView, 
    WantRestaurantListView, 
    WentRestaurantListView, 
    RestaurantListView, 
    TagCreateView, 
    RestaurantDeleteView, 
    RestaurantResetView,
    WentRestaurantDetailView,
    VisitUpdateView,
    VisitRevisitView,
)

app_name = "restaurants"

urlpatterns = [
    path("add/", RestaurantCreateView.as_view(), name="restaurant_add"),
    path("want/", views.WantRestaurantListView.as_view(), name="restaurant_list_want"),
    path("went/", views.WentRestaurantListView.as_view(), name="restaurant_list_went"),
    path("went/<int:pk>/", WentRestaurantDetailView.as_view(), name="restaurant_detail_went"),
    path("<int:pk>/", RestaurantDetailView.as_view(), name="restaurant_detail"),
    path("search/", RestaurantSearchView.as_view(), name="restaurant_search"),
    path('', RestaurantListView.as_view(), name='restaurant_list'),
    path('tags/add/', TagCreateView.as_view(), name='tag_add'),
    path("visit_chart/monthly/", views.visit_chart_monthly, name="visit_chart_monthly"),
    path("visit_chart/genre_top3/", views.visit_chart_top3_genre, name="visit_chart_top3_genre"),
    path("<int:pk>/delete/", RestaurantDeleteView.as_view(), name="restaurant_delete"),
    path("<int:pk>/reset/", RestaurantResetView.as_view(), name="restaurant_reset"),
    path("visit/<int:pk>/edit/", VisitUpdateView.as_view(), name="visit_edit"),
    path("visit/<int:pk>/revisit/", VisitRevisitView.as_view(), name="visit_revisit"),
    path("sub_mypage/", views.mypage, name="sub_mypage"),
    path("visit_chart/genre/", views.visit_chart_genre, name="visit_chart_genre"),
]

