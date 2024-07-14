from django.contrib import admin
from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('compare/', views.compare_cases_and_warehouse_view, name='compare_view'),
    path('add-new/', views.add_new, name='add_new'),
    path('receiving/image/', views.receiving_image, name='receiving_image'),
    path('receiving/', views.receiving, name='receiving'),
    path('receiving/search/', views.receiving_search, name='receiving_search'),
    path('delivery/excel', views.delivery_add_data, name='delivery_add_data'),
    path('delivery/', views.delivering, name='delivering'),
    path('delivery/image/', views.delivering_image, name='delivering_image'),    
    path('', views.index, name='index'),
]
