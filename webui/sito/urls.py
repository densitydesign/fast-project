from django.contrib import admin
from django.conf.urls import *
from django.urls import path
from sito import views

urlpatterns = [
    path('imposta-filtri/', views.imposta_filtri, name='imposta-filtri'),
    path('change-section/', views.change_section, name='change-section'),
    url('brand-hashtags.json/(?P<id_community>[0-9]+)', views.brand_hashtags_json, name='brand-hashtags-json'),
    url('brand-hashtags.json', views.brand_hashtags_json, name='brand-hashtags-json'),
    url('brand-hashtags', views.brand_hashtags, name='brand-hashtags'),
    url('brand-time', views.brand_time, name='brand-time'),
    url('brand-content', views.brand_content, name='brand-content'),
    path('community-definition/', views.community_definition, name='community-definition'),
    url('community/(?P<id_community>[0-9]+)/(?P<tipo>.*)?$', views.community_detail, name='community-detail'),
    url('community/(?P<id_community>[0-9]+)', views.community_detail, name='community-detail'),
    path('community/', views.community, name='community'),
    #path('community/test/', views.community_detail, name='community-detail'),
    path('', views.brand_content, name='brand'),
]
