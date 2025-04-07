from django.urls import path
from . import views

urlpatterns = [
    path('', views.tracker_list, name='tracker_list'),
    path('<int:product_id>', views.tracker_detail, name='tracker_detail'),
]
