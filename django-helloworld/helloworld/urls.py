from django.contrib import admin
from django.urls import path, include # Added include
from hello import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # This line connects all URLs from the 'hello' app.
    # It makes everything accessible via /hello/ (e.g., /hello/statistics/)
    path('hello/', include('hello.urls')),

    # This keeps your main landing page at the very root (/)
    path('', views.index_view, name='index'),
]