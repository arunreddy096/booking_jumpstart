from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
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

from django.core.mail import EmailMessage
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


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    # def save(self, domain_override=None,
    #          subject_template_name=None,
    #          email_template_name='registration/password_reset_email.html',
    #          use_https=False, token_generator=None,
    #          from_email=None, request=None, html_email_template_name='registration/password_reset_email.html'):

    def save(self, domain_override=None, subject_template_name=None,
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=None, from_email=None, request=None, **kwargs):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        user = Customer.objects.filter(email=email).first()
        if not user:
            return False

        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        subject = 'Password Reset Requested'
        email_template_name = 'registration/password_reset_email.html'
        html_email_template_name = 'registration/password_reset_email.html'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        # context = {
        #     'email': email,
        #     'domain': domain,
        #     'site_name': site_name,
        #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        #     'user': user,
        #     'token': token_generator.make_token(user),
        #     'protocol': 'https' if use_https else 'http',
        # }
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
        #
        # try:
        #     sendgrid_client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        #     sendgrid_message = Mail(
        #         from_email=from_email,
        #         to_emails=[to_email],
        #         subject=subject,
        #         html_content=html_email)
        #     response = sendgrid_client.send(sendgrid_message)
        #     print(response.status_code)
        # except Exception as e:
        #     print(e)

        # subject = render_to_string(subject_template_name, context)
        # # Email subject *must not* contain newlines
        # subject = ''.join(subject.splitlines())
        # email_body = render_to_string(email_template_name, context)
        # email_message = EmailMessage(
        #     subject=subject,
        #     body=email_body,
        #     from_email=from_email,
        #     to=[email],
        #     headers={'Reply-To': from_email}
        # )
        # email_message.content_subtype = "html"
        # email_message.send()
        #
        return super().save(
            domain_override=domain_override,
            subject_template_name=subject_template_name,
            email_template_name=email_template_name,
            use_https=use_https,
            token_generator=token_generator,
            from_email=from_email,
            request=request,
            **kwargs
        )



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