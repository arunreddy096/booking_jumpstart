from allauth.account.views import email
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate
from .forms import LoginForm, RegistrationForm, Forgot, BookingForm
from .models import Booking, Customer, User


# Create your views here.


class LoginSignup(View):
    def get(self, request):
        user_session = LoginForm()
        user_signup = RegistrationForm()
        context = {'form': user_session, 'signup': user_signup}
        return render(request, 'login.html', context)

    def post(self, request):
        form = LoginForm(request.POST)
        user_signup = RegistrationForm(request.POST)
        if form.is_valid() and 'first_name' not in request.POST.keys():
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is None:
                messages.error(request, "Incorrect username or password")
                return render(request, 'login.html', {'form': form})
            request.session['user_id'] = user.id
            return render(request, 'new_home.html', {'form': form, 'user': user})

        elif user_signup.is_valid():
            user_signup.save()
            form.email = user_signup.cleaned_data['email']
            return render(request, 'login.html', {'form': form})
        else:
            messages.error(request, "Please enter a Strong password")
            user_signup.first_name = user_signup.cleaned_data['first_name']
            user_signup.last_name = user_signup.cleaned_data['last_name']
            user_signup.email = user_signup.cleaned_data['email']
            context = {'form': LoginForm(), 'signup': user_signup}
            return render(request, 'login.html', context)


class Welcome(View):
    def get(self, request):
        return render(request, 'new_home.html')


class ForgotPassword(View):

    def get(self, request):
        user_forgot = Forgot()
        reset = None
        context = {'form': user_forgot, 'reset': reset}
        return render(request, 'forgot_password.html', context)

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
    template_name = 'jumpstart/bookingpage.html'

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