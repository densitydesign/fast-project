from django.contrib import admin
from django.conf.urls import *
from django.urls import path
from sito import views

urlpatterns = [
    path('change-section/', views.change_section, name='change-section'),
    path('brand/', views.home, name='brand'),
    path('community-definition/', views.community_definition, name='community-definition'),
    url('community/(?P<id_community>\w+)', views.community_detail, name='community-detail'),
    path('community/', views.community, name='community'),
    #path('community/test/', views.community_detail, name='community-detail'),
]
