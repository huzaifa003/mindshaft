from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),  # List and create blogs
    path('<int:blog_id>/', views.blog_detail, name='blog_detail'),  # Retrieve, update, delete a blog
    path('filter/', views.filter_blogs_by_date, name='filter_blogs_by_date'),  # Filter blogs by date
]
