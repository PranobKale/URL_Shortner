from django.urls import path
from . import views

urlpatterns = [
    path('shorten/', views.shorten_url, name='shorten'),
    path('<slug:short_url>/', views.redirect_to_original, name='redirect_to_original'),
    path('analytics/<str:short_url>/', views.analytics, name='analytics_view'),
    path('', views.index, name='index'),
]
