# tracking/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('livreurs/', views.livreurs_view, name='livreurs'),
    path('livreurs/<str:livreur_id>/', views.livreur_detail_view, name='livreur_detail'),
    path('positions/', views.positions_view, name='positions'),
    path('livreurs/<str:livreur_id>/positions/', views.livreur_positions_view, name='livreur_positions'),
]