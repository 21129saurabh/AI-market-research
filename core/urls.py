from django.contrib import admin
from django.urls import path
from research import views
from research.views import index, chat_api, save_user_details
from core import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('test/', views.test, name='test'),
    path('test1/', views.test1, name='test1'),
    path('api/chat/', chat_api, name='chat_api'),
    path('api/user/', save_user_details, name='save_user_details'),
    path('api/search/', views.search_api, name='search_api'),

    # ✅ Add this process-ingestion path here directly
    path('process-ingestion/<int:file_id>/', views.process_ingestion, name='process_ingestion'),

]
urlpatterns += [
    path('bulk-upload/<int:website_id>/', views.bulk_upload_view, name='bulk_upload'),

]

# ✅ Static media serving
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
