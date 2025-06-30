from research.views import index, chat_api, save_user_details
from django.urls import path  # ✅ Already correct, nothing to fix here.
from django.contrib import admin
from research import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
     path("test/", views.test, name="test"),
     path("test1/", views.test1, name="test1"),
    path('api/chat/', chat_api, name='chat_api'),
    path('api/user/', save_user_details, name='save_user_details'),
    path('api/search/', views.search_api, name='search_api'),
]

