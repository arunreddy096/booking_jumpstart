import random, string
import re
from pprint import pprint
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_encode

from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import UpdateView

from .forms import LoginForm, RegistrationForm, TicketForm, UpdateForm
from .models import Customer, User, Ticket, Event

# email imports
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site


# Create your views here.


class LoginSignup(View):
    def get(self, request):
        user_session = LoginForm()
        user_signup = RegistrationForm()
        context = {'form': user_session, 'signup': user_signup}
        return render(request, 'registration/login_page.html', context)

    def post(self, request):
        form = LoginForm(request.POST)
        user_signup = RegistrationForm(request.POST, request.FILES)
        if form.is_valid() and 'first_name' not in request.POST.keys():
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is None:
                user_signup = RegistrationForm()
                messages.error(request, "Incorrect E-mail or password")
                return render(request, 'registration/login_page.html', {'form': form, 'signup': user_signup})
            print(user, type(user))
            # request.session['user_id'] = user.id
            login(request, user)
            # request.session.save()
            return HttpResponseRedirect(reverse('welcome'))
            # return render(request, 'home_page.html', {'form': form, 'user': user})

        elif user_signup.is_valid():
            print('user sign in form is valid')
            user_signup.save()
            form = LoginForm(initial={
                'email': user_signup.cleaned_data['email']
            })
            return render(request, 'registration/login_page.html', {'form': form})
        else:
            print('user sign in not valid')
            messages.error(request, "Please enter a Strong password")
            user_signup.first_name = user_signup.cleaned_data['first_name']
            user_signup.last_name = user_signup.cleaned_data['last_name']
            user_signup.email = user_signup.cleaned_data['email']
            context = {'form': LoginForm(), 'signup': user_signup}
            return render(request, 'registration/login_page.html', context)


class Welcome(View):
    def get(self, request):
        user_id = request.session.get('_auth_user_id')

        # checking for social auth login directly
        user = request.user
        if user.is_authenticated:
            print(f'Social authentication by {user.username}-{user.email}')
            try:
                user = Customer.objects.get(email=user.email)
            except ObjectDoesNotExist:
                print('Social auth user is not as a customer, making him as a customer')
                try:
                    new_customer = Customer(
                        user=request.user,
                        username=user.username,
                        email=user.email,
                        profile_image='images/profile/gojo.png',
                        password=make_password("".join(random.choices(string.ascii_letters + string.digits, k=8)))
                    )
                    new_customer.save()
                    print(f'Cusomter saved')
                except Exception as e:
                    print(f'Cusomter didnt saved {e}')
                user = Customer.objects.get(email=user.email)

            finally:
                login(request, user, backend='jumpstart.backends.EmailAuthBackend')
                # request.session['_auth_user_id'] = user.id
                return render(request, 'home_page.html', {'user': user})
        elif user_id is not None:
            # print(user_id, type(user_id), request.session.get('_auth_user_id'))
            user = get_object_or_404(Customer, id=user_id)
            # user = User.objects.get(id=request.session.get('user_id'))
            print(user, type(user))
            return render(request, 'home_page.html', {'user': user})
        else:
            return render(request, 'home_page.html', {})


class Profile(View):

    def get(self, request):
        print('in get profile')
        user_id = request.session.get('_auth_user_id')
        user = get_object_or_404(Customer, id=user_id)
        tickets = Ticket.objects.filter(customer=user).order_by('-transaction_timestamp')
        print(tickets)
        # updateform = UpdateForm()
        return render(request, 'profile_page.html', {'user': user, 'tickets': tickets,})# 'form':updateform})

    def post(self, request):
        print('in post profile')
        # updateform = UpdateForm(request.POST)
        #
        # if not request.POST:
        #     # delete the user
        #     user_id = request.session.get('_auth_user_id')
        #     print(user_id)
        #     user = get_object_or_404(Customer, id=user_id)
        #     print('on post delete: ', user)
        #     messages.success(request, 'Your account has been deleted.')
        #     logout(request)
        #     user.delete()
        #     return redirect('home')
        # else:
        #     return redirect('profile_update')

        # delete the user
        user_id = request.session.get('_auth_user_id')
        print(user_id)
        user = get_object_or_404(Customer, id=user_id)
        print('on post delete: ', user)
        messages.success(request, 'Your account has been deleted.')
        logout(request)
        user.delete()
        return redirect('login')


class UserLogout(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('welcome'))


class CustomerBooking(View):

    def get(self, request):
        user_id = request.session.get('_auth_user_id')
        user = get_object_or_404(Customer, id=user_id)
        print('got' ,user, messages)
        form = TicketForm()
        events = Event.objects.all()

        return render(request, 'booking_page.html', {'form': form, 'user': user, 'events': events})

    def post(self, request):
        print(f'booking post received')
        form = TicketForm(request.POST)
        user_id = request.session.get('_auth_user_id')
        user = get_object_or_404(Customer, id=user_id)
        events = Event.objects.all()
        if form.is_valid():
            print('valid form')
            form.save(commit=False)
            event_type = form.cleaned_data['event_type']
            customer = user
            reserved_event = form.cleaned_data['event']
            if reserved_event is None:
                reserved_event = form.cleaned_data['event_multi']
            reservation_date = form.cleaned_data['reservation_date']
            reservation_time = form.cleaned_data['reservation_time']
            is_student = form.cleaned_data['is_student']
            university = form.cleaned_data['university']
            adult_tickets = form.cleaned_data['adult_tickets']
            children_tickets = form.cleaned_data['children_tickets']
            total_price = float(form.cleaned_data['total_price'].replace('$', ''))
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            province = form.cleaned_data['province']
            phone_number = form.cleaned_data['phone_number']
            ticket_id = "T_" + "".join(random.choices(string.ascii_letters + string.digits, k=4))
            transaction_id = "TX_" + "".join(random.choices(string.ascii_letters + string.digits, k=14))
            # pprint([(x, y) for x, y in form.cleaned_data.items()])
            #
            # print(f'form validated: checking other validaitons:\n{reserved_event}\n{reservation_time}\n{reservation_date}')
            # checking each event capacity for that time
            get_details_from_db = Ticket.objects.filter(
                event_type=event_type,
                reserved_event=reserved_event,
                reservation_time=reservation_time,
                reservation_date=reservation_date
            )
            if get_details_from_db.count() >= 5:
                messages.error(request,
                               f"{reserved_event} event booked full for this slot {reservation_time} on \
                               {reservation_date}. Please choose another slot!")
                return render(request, 'booking_page.html', {'form': form, 'user': user, 'events': events})

            # checking abnormal ticket conditions
            if children_tickets and not adult_tickets:
                if reserved_event.name != 'Arcade Corner':
                    messages.error(request,
                                   f"Atleast 1 adult ticket should be booked for all the events except Arcade Corner")
                    return render(request, 'booking_page.html', {'form': form, 'user': user, 'events': events})
            elif not children_tickets and not adult_tickets:
                messages.error(request,
                               f"Atleast 1 ticket should be booked, Empty booking is not allowed")
                return render(request, 'booking_page.html', {'form': form, 'user': user, 'events': events})


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
                total_price=total_price,
                address=address,
                city=city,
                province=province,
                phone_number=phone_number,
                ticket_id=ticket_id,
                transaction_id=transaction_id,
                transaction_timestamp=timezone.now()
            )
            new_ticket.save()

            subject = 'DO NOT REPLY - Jumpstart - Reservation'
            email_template_name = 'registration/booking_confirm.html'
            html_email_template_name = 'registration/booking_confirm.html'
            from_email = settings.DEFAULT_FROM_EMAIL
            print('from mail ', from_email)
            to_email = user.email
            ticket = Ticket.objects.get(ticket_id=ticket_id)
            context = {
                'email': to_email,
                'site_name': 'Jumpstart',
                'user': user,
                'ticket': ticket
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

            messages.success(request, 'Booking Successful and Email is sent')
            return render(request, 'booking_success.html')
        else:
            print('invalid form')

            print(form.errors)
            return render(request, 'booking_page.html', {'form': form, 'user': user, 'events': events})


class Search(View):

    def get(self, request, id):

        results = Event.objects.filter(
            Q(id__icontains=id)
        )
        return render(request, 'search.html', {'results': results})

    def post(self, request, id):
        # print('in search post')
        query = request.POST.get('q')
        print(f'got search query, splitting = {query.split()}')
        results = Event.objects.filter(Q(keywords__icontains=query))
        # print(results)
        return render(request, 'search.html', {'results': results, 'query': query})


class CustomerUpdateView(UpdateView):

    model = Customer
    form_class = UpdateForm
    template_name = 'profile_page.html'
    success_url = reverse_lazy('view_profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_object_or_404(Customer, id=self.request.session.get('_auth_user_id'))
        return context

    def form_valid(self, form):
        # Check whether the entered password contains at least one uppercase, one lowercase, one digit, and one special character
        if not re.search(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$',
                         form.cleaned_data['password']):
            form.errors['password'] = [
                'Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.']
            return self.form_invalid(form)
        form.instance.password = make_password(form.cleaned_data['password'])
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error in your submission.')
        return super().form_invalid(form)

    def get_object(self, queryset=None):
        return get_object_or_404(Customer, id=self.request.session.get('_auth_user_id'))



