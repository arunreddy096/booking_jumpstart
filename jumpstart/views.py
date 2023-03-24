from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .forms import LoginForm, RegistrationForm, TicketForm
from .models import Booking, Customer, User


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
            print(user, user.profile_image, type(user))
            request.session['user_id'] = user.id
            login(request, user)
            return HttpResponseRedirect(reverse('welcome'))
            # return render(request, 'new_home.html', {'form': form, 'user': user})

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
        user_id = request.session.get('_auth_user_id')
        # print(user_id)
        if user_id is not None:
            # print(user_id, type(user_id), request.session.get('_auth_user_id'))
            user = Customer.objects.get(id=user_id)
            # user = User.objects.get(id=request.session.get('user_id'))
            print(user, type(user))
            return render(request, 'new_home.html', {'user': user})
        else:
            return render(request, 'new_home.html', {})


# class CreateBookingView(View):
#     form_class = BookingForm
#     template_name = 'bookingpage.html'
#
#     # @login_required()
#     def get(self, request, *args, **kwargs):
#         user_id = request.session.get('user_id')
#         user = User.objects.get(id=user_id)
#         form = self.form_class()
#         return render(request, self.template_name, {'form': form, 'user': user})
#
#     @login_required()
#     def post(self, request, *args, **kwargs):
#         user_id = request.session.get('user_id')
#         user = User.objects.get(id=user_id)
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             form.save()
#             message = "booking successful"
#             print(user_id)
#             return render(request, 'bookingpage.html', {'user': user})
#             # return redirect('jumpstart/bookingpage.html', message, )
#         return render(request, self.template_name, {'form': form})


class Profile(View):

    def get(self, request):
        user_id = request.session.get('_auth_user_id')
        user = Customer.objects.get(id=user_id)
        return render(request, 'profile.html', {'user': user})

    def post(self, request):
        print('on post delete: ', request.session['user_id'])
        messages.success(request, 'Your account has been deleted.')
        # return redirect('home')
        return render(request, 'login2.html', )


class UserLogout(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('welcome'))


class CustomerBooking(View):

    def get(self, request):
        user_id = request.session.get('_auth_user_id')
        user = Customer.objects.get(id=user_id)
        form = TicketForm()
        return render(request, 'booking2.html', {'form': form})
