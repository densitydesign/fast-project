from django.contrib import admin
from django.urls import path
from sito import views

urlpatterns = [
    path('brand/', views.home, name='brand'),
    path('community/', views.community, name='community'),
    # path('community/<str:category>/$', views.CommunityDetail, name='community-detail'),
    path('community/test/', views.CommunityDetail, name='community-detail'),
]
