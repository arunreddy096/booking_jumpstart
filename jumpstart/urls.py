from django.urls import path, reverse_lazy

# View-related imports
from . import views
from django.contrib.auth import views as reset_views

# Django settings-related imports
from django.conf import settings
from django.conf.urls.static import static

# Form-related imports
from .forms import CustomPasswordResetForm


app_name = 'jumpstart'
urlpatterns = [
    path('login/', views.LoginSignup.as_view(), name='login'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('', views.Welcome.as_view(), name='welcome'),
    path('booking/create/', views.CustomerBooking.as_view(), name='create_booking'),
    path('view_profile/', views.Profile.as_view(), name='view_profile'),
    path('view_profile/update/', views.CustomerUpdateView.as_view(), name='profile_update'),
    path('search/<int:id>', views.Search.as_view(), name='search'),

    # forgot password views
    path('password_reset/',
         reset_views.PasswordResetView.as_view(form_class=CustomPasswordResetForm,
                                               success_url=reverse_lazy('jumpstart:password_reset_done')),
         name='password_reset',
        ),
    path('password_reset/done/',
         reset_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         reset_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html',
                                                      success_url=reverse_lazy('jumpstart:password_reset_complete')),
         name='password_reset_confirm'),
    path('reset/done/', reset_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
