# Authentication and User management
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ObjectDoesNotExist

# Email and Template Rendering
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Forms and Form Fields
from django.forms import ModelForm, TextInput, EmailInput, PasswordInput
from django import forms

# URL Handling and Settings
from django.urls import reverse, reverse_lazy
from django.conf import settings

# Models
from .models import Customer, Event, Ticket

# Utilities
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from django.utils.html import strip_tags


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
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'profile_image']
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
            'profile_image': _('profile_image*'),
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = PasswordInput(
            attrs={'class': 'pass'})
        self.fields['password2'].widget = PasswordInput(
            attrs={'class': 'passConfirm'})
        self.fields['profile_image'].widget.attrs['required'] = True

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
            password=make_password(self.cleaned_data['password1']),
            profile_image=self.cleaned_data['profile_image']
        )

        print(new_customer)
        new_customer.save()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            if Customer.objects.get(email=email):
                raise forms.ValidationError('Email already registered. Please use another email')
        except ObjectDoesNotExist:
            return email


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))

    def save(self, domain_override=None, subject_template_name=None,
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=None, from_email=None, request=None, **kwargs):

        user = authenticate(email=self.cleaned_data['email'])
        print(user)
        print('validating email submitted', user, user.pk)
        subject = 'Password Reset Requested'
        email_template_name = 'registration/password_reset_email.html'
        html_email_template_name = 'registration/password_reset_email.html'
        from_email = settings.DEFAULT_FROM_EMAIL
        print('from mail ', from_email)
        to_email = user.email
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        reset_url = '{}://{}{}'.format(
            'https' if use_https else 'http',
            domain,
            reverse_lazy('jumpstart:password_reset_confirm', kwargs={'uidb64': uid, 'token': token}, )
        )

        print(reset_url)
        context = {
            'email': to_email,
            'domain': domain,
            'site_name': 'Jumpstart',
            'uid': uid,
            'user': user,
            'token': token,
            'reset_url': reset_url,
            'protocol': 'https' if use_https else 'http',
        }
        email = render_to_string(email_template_name, context)
        html_email = render_to_string(html_email_template_name, context)

        # Create the email message
        msg = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(email),
            from_email=from_email,
            to=[to_email],
        )
        # Attach the HTML version of the email
        msg.attach_alternative(html_email, 'text/html')

        # Send the email using the SMTP backend
        msg.send()


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'aria-describedby': 'new_password_help_text'
        }),
        help_text="Your password must contain at least 8 characters.",
    )

    new_password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'aria-describedby': 'confirm_password_help_text'
        }),
        help_text="Enter the same password as before, for verification.",
    )


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        exclude = ['reserved_event', 'ticket_id', 'transaction_id', 'customer', 'total_price', 'transaction_timestamp']

        widgets = {
            'event_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'event-type',
                'name': 'event-type',
                'required': True,
            }),
            'reservation_date': forms.TextInput(attrs={
                'class': 'form-control flatpickr-input',
                'id': 'booking-date',
                'required': True,
            }),
            'reservation_time': forms.Select(attrs={
                'class': 'form-control',
                'id': 'event-time',
            }),
            'is_student': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'student',
            }),
            'university': forms.Select(attrs={
                'class': 'form-control',
                'id': 'university',
                'onchange': 'resizeUniversitySelect(this)'
            }),
            'adult_tickets': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'adult-tickets',
            }),
            'children_tickets': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'children-tickets',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'address',
                'required': True,
            }),
            'city': forms.Select(attrs={
                'class': 'form-control',
                'id': 'city',
                'required': True,
            }),
            'province': forms.Select(attrs={
                'class': 'form-control',
                'id': 'province',
                'required': True,
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'phone-number',
                'required': True,
            }),
        }

    EVENT_TYPE_CHOICES = [
        ('single-event', 'Single Event'),
        ('multi-event', 'Multi Event'),
    ]

    event = forms.ModelChoiceField(required=False,
                                   queryset=Event.objects.filter(event_type='single'),
                                   # queryset=Event.objects.all(),
                                   to_field_name='name',
                                   widget=forms.Select(attrs={
                                       'class': 'form-control',
                                       'id': 'event-name-single'
                                   })
                                   )
    event_multi = forms.ModelChoiceField(required=False,
                                         queryset=Event.objects.filter(event_type='multi'),
                                         # queryset=Event.objects.all(),
                                         to_field_name='name',
                                         widget=forms.Select(attrs={
                                             'class': 'form-control',
                                             'id': 'event-name-multi'
                                         }))
    total_price = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'readonly': True,
                'id': 'total-price',
                'required': True,
            }))

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError('Please enter only digits for phone number')
        if len(phone_number) != 10:
            raise forms.ValidationError('Phone number should be exactly 10 digits long')
        return phone_number

    def clean_adult_tickets(self):
        adult_tickets = self.cleaned_data.get('adult_tickets')
        if adult_tickets < 0:
            raise forms.ValidationError('Please enter a positive number for adult tickets')
        return adult_tickets

    def clean_children_tickets(self):
        children_tickets = self.cleaned_data.get('children_tickets')
        if children_tickets < 0:
            raise forms.ValidationError('Please enter a positive number for children tickets')
        return children_tickets


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['username', 'first_name', 'last_name', 'password', 'profile_image']

        widgets = {
            # telling Django your password field in the mode is a password input on the template
            'username': TextInput(attrs={
                'class': 'form-control',
            }),
            'first_name': TextInput(attrs={
                'class': 'form-control',
            }),
            'last_name': TextInput(attrs={
                'class': 'form-control',
            }),
            'password': PasswordInput(attrs={
                'class': 'form-control',
            }),
        }
        help_texts = {
            'password': 'Your password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number.'
        }


class CancelTicket(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['ticket_id']

        widgets = {
            # telling Django your password field in the mode is a password input on the template
            'username': TextInput(attrs={
                'class': 'form-control',
            })
        }

    def clean_ticket_id(self):
        ticket_id = self.cleaned_data.get('ticket_id')
        print('here at tickets')
        try:
            get_ticket = Ticket.objects.get(ticket_id=ticket_id)
        except ObjectDoesNotExist:
            raise forms.ValidationError('Please enter a valid ticket id or You have zero orders')
        return ticket_id
