import random, string
from pprint import pprint
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy

from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .forms import LoginForm, RegistrationForm, TicketForm
from .models import Customer, User, Ticket


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
            user = get_object_or_404(Customer, id=user_id)
            # user = User.objects.get(id=request.session.get('user_id'))
            print(user, type(user))
            return render(request, 'new_home.html', {'user': user})
        else:
            return render(request, 'new_home.html', {})


class Profile(View):

    def get(self, request):
        user_id = request.session.get('_auth_user_id')
        user = get_object_or_404(Customer, id=user_id)
        return render(request, 'profile.html', {'user': user})

    def post(self, request):
        user_id = request.session.get('_auth_user_id')
        user = get_object_or_404(Customer, id=user_id)
        print('on post delete: ', request.session['user_id'])
        messages.success(request, 'Your account has been deleted.')
        user.delete()
        # return redirect('home')
        return render(request, 'login2.html', )


class UserLogout(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('welcome'))


class CustomerBooking(View):

    def get(self, request):
        user_id = request.session.get('_auth_user_id')
        user = get_object_or_404(Customer, id=user_id)
        form = TicketForm()
        return render(request, 'booking2.html', {'form': form, 'user':user})

    def post(self, request):
        print(f'booking post received')
        form = TicketForm(request.POST)
        user_id = request.session.get('_auth_user_id')
        user = get_object_or_404(Customer, id=user_id)
        if form.is_valid():
            print('valid form')
            form.save(commit=False)
            event_type = form.cleaned_data['event_type']
            customer = user
            reserved_event = form.cleaned_data['event']
            reservation_date = form.cleaned_data['reservation_date']
            reservation_time = form.cleaned_data['reservation_time']
            is_student = form.cleaned_data['is_student']
            university = form.cleaned_data['university']
            adult_tickets = form.cleaned_data['adult_tickets']
            children_tickets = form.cleaned_data['children_tickets']
            spl_adult_tickets = form.cleaned_data['spl_adult_tickets']
            spl_children_tickets = form.cleaned_data['spl_children_tickets']
            total_price = float(form.cleaned_data['total_price'].replace('$',''))
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            province = form.cleaned_data['province']
            phone_number = form.cleaned_data['phone_number']
            ticket_id = "T_" + "".join(random.choices(string.ascii_letters + string.digits, k=4))
            transaction_id = "TX_" + "".join(random.choices(string.ascii_letters + string.digits, k=14))
            pprint([(x,y) for x,y in form.cleaned_data.items()])
            new_ticket = Ticket(
                reserved_event=reserved_event,
                customer=customer,
                event_type=event_type,
                reservation_date=reservation_date,
                reservation_time=reservation_time,
                is_student=is_student,
                university=university,
                adult_tickets=adult_tickets,
                children_tickets=children_tickets,
                spl_adult_tickets=spl_adult_tickets,
                spl_children_tickets=spl_children_tickets,
                total_price=total_price,
                address=address,
                city=city,
                province=province,
                phone_number=phone_number,
                ticket_id=ticket_id,
                transaction_id=transaction_id,
            )
            new_ticket.save()
            return render(request, 'profile.html', {'user': user})
        else:
            print('invalid form')
            print(form.errors, )
            return render(request, 'booking2.html', {'form': form, 'user': user})

