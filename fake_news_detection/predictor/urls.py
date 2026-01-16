from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('check/', views.check_fact, name='check_fact') ,
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup') 
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
