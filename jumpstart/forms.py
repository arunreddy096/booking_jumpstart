from django.forms import ModelForm, TextInput, EmailInput, PasswordInput, forms
from .models import Customer, Booking
from django import forms
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.forms import UserCreationForm


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
            'first_name': _('first name'),
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
        username = self.cleaned_data['first_name'] + '_' + self.cleaned_data['last_name']
        new_customer = Customer(
            username=username,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            password=make_password(self.cleaned_data['password1'])
        )
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