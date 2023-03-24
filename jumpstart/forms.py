from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.forms import ModelForm, TextInput, EmailInput, PasswordInput
from django.utils.html import strip_tags

from .models import Customer, Event, Ticket
from django import forms
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.urls import reverse

from .city_n_provinces_n_edu import CITY_CHOICES, PROVINCE_CHOICES, UNIVERSITY_CHOICES, EVENT_TIME_CHOICES


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


# class BookingForm(ModelForm):
#     class Meta:
#         model = Booking
#         fields = [
#
#             'reserveDate',
#             'address',
#             'phoneNumber',
#             'adultTicketCount',
#             'ChildTicketCount',
#             'FastTrackAdultTicketCount',
#             'FastTrackChildTicketCount',
#             'SeniorCitizenTicketCount',
#             'AdultCollegeIdOfferTicketCount',
#             'totalPrice',
#         ]
#         widgets = {
#             'reserveDate': forms.DateInput(attrs={'type': 'date'}),
#         }


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
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}, )
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
        fields = ['event', 'reservation_type', 'reservation_date', 'address', 'city', 'province',
                  'phone_number', 'ticket_id', 'transaction_id']
        # widgets = {
        #     'reservation_date': forms.TextInput(attrs={
        #         'class': 'form-control flatpickr-input',
        #         'id': 'booking-date'
        #     }),
        #     'event': forms.ModelChoiceField(queryset=Event.objects.filter(event_type='single'))
        # }

    EVENT_TYPE_CHOICES = [
        ('single-event', 'Single Event'),
        ('multi-event', 'Multi Event'),
    ]

    event_type = forms.ChoiceField(choices=EVENT_TYPE_CHOICES,
                                   widget=forms.Select(
                                       attrs={
                                           'class': 'form-control',
                                           'id': 'event-type',
                                           'name': 'event-type',
                                       }))
    reservation_date = forms.DateField(widget=forms.TextInput(
        attrs={
            'class': 'form-control flatpickr-input',
            'id': 'booking-date',
        }))
    event = forms.ModelChoiceField(
        queryset=Event.objects.filter(event_type='single'),
        to_field_name='name',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'event-name'
        })
    )
    event_time = forms.ChoiceField(choices=EVENT_TIME_CHOICES,
                                   widget=forms.Select(
                                       attrs={
                                           'class': 'form-control',
                                           'id': 'event-time',
                                       }))

    is_student = forms.BooleanField(required=False,
                                    widget=forms.CheckboxInput(attrs={
                                        'class': 'form-check-input',
                                        'id': 'student',
                                    }))

    university = forms.ChoiceField(choices=UNIVERSITY_CHOICES,
                                   widget=forms.Select(
                                     attrs={
                                         'class': 'form-control',
                                         'id': 'university',
                                         'onchange': 'resizeUniversitySelect(this)'
                                     }))
    adult_tickets = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'id': 'adult-tickets',
            }))
    children_tickets = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'id': 'children-ticket'
            }))
    spl_adult_tickets = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'id': 'special-adult-tickets',
            }))
    spl_children_tickets = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'id': 'special-children-ticket'
            }))

    address = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'id': 'address',
        }))
    city = forms.ChoiceField(choices=CITY_CHOICES,
                             widget=forms.Select(
                                 attrs={
                                     'class': 'form-control',
                                     'id': 'city',
                                 }))
    province = forms.ChoiceField(choices=PROVINCE_CHOICES,
                                 widget=forms.Select(
                                     attrs={
                                         'class': 'form-control',
                                         'id': 'province',
                                     }))
    phone_number = forms.CharField(max_length=20,
                                   widget=forms.TextInput(
                                       attrs={
                                           'class': 'form-control',
                                           'id': 'phone-number',
                                       }))
    total_price = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'disabled': True,
                'id': 'total-price',
            }))

    # reservation_type = forms.ChoiceField(choices=Ticket.RESERVATION_CHOICES, widget=forms.RadioSelect())
    # reservation_time = forms.TimeField(widget=forms.TimeInput(format='%I:%M %p', attrs={'class': 'form-control'}))
    # address = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # city = forms.ChoiceField(choices=CITY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    # province = forms.ChoiceField(choices=PROVINCE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    # phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # ticket_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # transaction_id = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # university = forms.ChoiceField(choices=UNIVERSITY_CHOICES, required=False,
    #                                widget=forms.Select(attrs={'class': 'form-control student'}))
    #
    # adult_tickets = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control multi-event'}))
    # children_tickets = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control multi-event'}))
    # special_adult_tickets = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control multi-event'}))
    # special_children_tickets = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control multi-event'}))

    # class Meta:
    #     model = Ticket
    #     fields = ['event', 'reservation_type', 'reservation_date', 'reservation_time', 'address', 'city', 'province',
    #               'phone_number', 'ticket_id', 'transaction_id', 'university', 'adult_tickets', 'children_tickets',
    #               'special_adult_tickets', 'special_children_tickets']
