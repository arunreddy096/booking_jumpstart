from django.contrib.auth import authenticate
from django.forms import ModelForm, TextInput, EmailInput, PasswordInput, forms
from django.utils.html import strip_tags

from .models import Customer, Booking
from django import forms
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.forms import UserCreationForm, PasswordResetForm

from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, Personalization, Content

from django.urls import reverse



class LoginForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['email', 'password']
        widgets = {
            # telling Django your password field in the mode is a password input on the template
            'email': EmailInput(attrs={
                'required': True,
                'class': 'email_login'
            }),
            'password': PasswordInput(attrs={
                'required': True,
            })
        }
        labels = {
            'email': _('Email'),
            'password': _('Password')
        }


class RegistrationForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            # telling Django your password field in the mode is a password input on the template
            'first_name': TextInput(attrs={
                'required': True,
                'class': 'name',
            }),
            'email': EmailInput(attrs={
                'required': True,
                'class': 'email'
            }),
            'password1': PasswordInput(attrs={
                'required': True,
                'class': 'pass'
            }),
            'password2': PasswordInput(attrs={
                'required': True,
            }),
        }
        labels = {
            'first_name': _('first name*'),
            'last_name': _('last name'),
            'email': _('email*'),
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = PasswordInput(
            attrs={'class': 'pass'})
        self.fields['password2'].widget = PasswordInput(
            attrs={'class': 'passConfirm'})

        for fieldname in ['first_name', 'last_name', 'email']:
            self.fields[fieldname].help_text = None

    def save(self, commit=True):
        print('in save function')
        username = self.cleaned_data['first_name'] + '_' + self.cleaned_data['last_name']
        new_customer = Customer(
            username=username,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            password=make_password(self.cleaned_data['password1'])
        )
        print(new_customer)
        new_customer.save()


class Forgot(UserCreationForm):
    class Meta:
        model = Customer
        fields = ['email', 'password1', 'password2']
        widgets = {
            # telling Django your password field in the mode is a password input on the template
            'email': EmailInput(attrs={
                'placeholder': 'enter a valid email',
            })
        }

    def __init__(self, *args, **kwargs):
        super(Forgot, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = PasswordInput(
            attrs={'placeholder': 'enter your password'})
        self.fields['password2'].widget = PasswordInput(
            attrs={'placeholder': 're-enter your password'})

        # self.fields['email'].help_text = None

    def clean(self):
        pass


class ResetPassword(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(ResetPassword, self).__init__(*args, **kwargs)

    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'type': 'email',
        'placeholder': 'enter email id'
    }))

    template_name = 'registration/password_reset_form.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_done')


class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = [

            'reserveDate',
            'address',
            'phoneNumber',
            'adultTicketCount',
            'ChildTicketCount',
            'FastTrackAdultTicketCount',
            'FastTrackChildTicketCount',
            'SeniorCitizenTicketCount',
            'AdultCollegeIdOfferTicketCount',
            'totalPrice',
        ]
        widgets = {
            'reserveDate': forms.DateInput(attrs={'type': 'date'}),
        }