from django.urls import path, include
from . import views
from .views import CreateBookingView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.LoginSignup.as_view(), name='login'),
    path('', views.Welcome.as_view(), name='welcome'),
    path('forgot_password/', views.ForgotPassword.as_view(), name='forgot'),
    path('booking/create/', CreateBookingView.as_view(), name='create_booking'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
