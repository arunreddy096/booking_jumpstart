from django.urls import path, include
from . import views
from .views import CreateBookingView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as reset_views
from .forms import ResetPassword

urlpatterns = [
    path('login/', views.LoginSignup.as_view(), name='login'),
    path('', views.Welcome.as_view(), name='welcome'),
    # path('forgot_password/', views.ForgotPassword.as_view(), name='forgot'),
    path('booking/create/', CreateBookingView.as_view(), name='create_booking'),

    # reset password
    path('password_reset/',
         # reset_views.PasswordResetView.as_view(template_name='registration/password_reset_email.html',
         #                                       form_class=ResetPassword),
         # name='password_reset'),
         views.SendPass.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/',
         reset_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password_reset/done/',
         reset_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/done/', reset_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
