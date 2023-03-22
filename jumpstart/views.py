from allauth.account.views import email
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate
from sendgrid import SendGridAPIClient, Mail

from .forms import LoginForm, RegistrationForm, Forgot, BookingForm, PasswordResetForm
from .models import Booking, Customer, User


from django.conf import settings
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


# Create your views here.


class LoginSignup(View):
    def get(self, request):
        user_session = LoginForm()
        user_signup = RegistrationForm()
        context = {'form': user_session, 'signup': user_signup}
        return render(request, 'login2.html', context)

    def post(self, request):
        form = LoginForm(request.POST)
        user_signup = RegistrationForm(request.POST)
        if form.is_valid() and 'first_name' not in request.POST.keys():
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is None:
                user_signup = RegistrationForm()
                messages.error(request, "Incorrect username or password")
                return render(request, 'login2.html', {'form': form, 'signup': user_signup})
            print(user, user.profile_image)
            request.session['user_id'] = user.id
            return render(request, 'new_home.html', {'form': form, 'user': user})

        elif user_signup.is_valid():
            print('user sign in form is valid')
            user_signup.save()
            form = LoginForm(initial={
                'email': user_signup.cleaned_data['email']
            })
            return render(request, 'login2.html', {'form': form})
        else:
            print('user sign in not valid')
            messages.error(request, "Please enter a Strong password")
            user_signup.first_name = user_signup.cleaned_data['first_name']
            user_signup.last_name = user_signup.cleaned_data['last_name']
            user_signup.email = user_signup.cleaned_data['email']
            context = {'form': LoginForm(), 'signup': user_signup}
            return render(request, 'login2.html', context)


class Welcome(View):
    def get(self, request):
        return render(request, 'new_home.html')


class ForgotPassword(View):

    def get(self, request):
        user_forgot = Forgot()
        reset = None
        context = {'form': user_forgot, 'reset': reset}
        return render(request, 'registration/password_reset_form.html', context)

    def post(self, request):
        form = Forgot(request.POST)
        reset = None
        if form.is_valid():
            user = authenticate(email=form.cleaned_data['email'])
            user.set_password(form.cleaned_data['password1'])
            user.save()
            return HttpResponseRedirect(reverse('login'))
        elif reset is None:
            user = authenticate(email=form.cleaned_data['email'])
            if user is None:
                messages.error(request, "Incorrect email")
                return render(request, 'forgot_password.html', {'form': form, 'reset': reset})
            else:
                reset = Forgot()
                reset.initial['email'] = form.cleaned_data['email']
                messages.success(request, "proceed to reset")
                return render(request, 'forgot_password.html', {'reset': reset})


class CreateBookingView(View):
    form_class = BookingForm
    template_name = 'bookingpage.html'

    # @login_required()
    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        user = User.objects.get(id=user_id)
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'user': user})

    @login_required()
    def post(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        user = User.objects.get(id=user_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            message = "booking successful"
            print(user_id)
            return render(request, 'bookingpage.html', {'user': user})
            # return redirect('jumpstart/bookingpage.html', message, )
        return render(request, self.template_name, {'form': form})

class SendPass(View):
    def get(self, request):
        form = PasswordResetForm()
        return render(request, 'registration/password_reset_form.html', {'form': form,})

    def post(self, request):
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = authenticate(email=form.cleaned_data['email'])
            print(user)
            print('validating email submitted', user, user.pk)
            subject = 'Password Reset Requested'
            email_template_name = 'registration/password_reset_email.html'
            html_email_template_name = 'registration/password_reset_email.html'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = user.email
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            print(reset_url)
            context = {
                'email': to_email,
                'domain': self.request.META['HTTP_HOST'],
                'site_name': 'Jumpstart',
                'uid': uid,
                'user': user,
                'token': token,
                'reset_url': self.request.build_absolute_uri(reset_url),
                'protocol': 'https' if self.request.is_secure() else 'http',
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
            # msg.send()

            try:
                sendgrid_client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
                sendgrid_message = Mail(
                    from_email=from_email,
                    to_emails=[to_email],
                    subject=subject,
                    html_content=html_email)
                response = sendgrid_client.send(sendgrid_message)
                print(response.status_code)
            except Exception as e:
                print(e.message)

            return redirect('password_reset_done')
