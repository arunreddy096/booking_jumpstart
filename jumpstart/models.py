from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Customer(User):
    class Meta:
        ordering = ['first_name']
        verbose_name_plural = 'customer'

    profile_image = models.ImageField(upload_to='images/profile/', default='gojo.png')

    def __str__(self):
        return self.username


class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    bookingDate = models.DateField(auto_now=True)
    reserveDate = models.DateField()
    address = models.CharField(max_length=100)
    phoneNumber = models.CharField(max_length=20)
    totalPrice = models.PositiveIntegerField(default=0)
    adultTicketCount = models.PositiveIntegerField(default=0)
    ChildTicketCount = models.PositiveIntegerField(default=0)
    FastTrackAdultTicketCount = models.PositiveIntegerField(default=0)
    FastTrackChildTicketCount = models.PositiveIntegerField(default=0)
    SeniorCitizenTicketCount = models.PositiveIntegerField(default=0)
    AdultCollegeIdOfferTicketCount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.customer.first_name} your booking is successful on {self.reserveDate}'


class Event(models.Model):
    SINGLE_EVENT = 'single'
    MULTI_EVENT = 'multi'
    EVENT_TYPE_CHOICES = [
        (SINGLE_EVENT, 'Single Event'),
        (MULTI_EVENT, 'Multi Event'),
    ]
    name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timings = models.CharField(max_length=100)
    short_description = models.CharField(max_length=200)
    additional_info = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    RESERVATION_CHOICES = [
        ('S', 'Single Event'),
        ('M', 'Multi Event')
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    reservation_type = models.CharField(max_length=1, choices=RESERVATION_CHOICES)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    ticket_id = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.event} - {self.ticket_id}"

