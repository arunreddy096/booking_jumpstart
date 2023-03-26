import datetime
import re

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import lower

from .city_n_provinces_n_edu import CITY_CHOICES, PROVINCE_CHOICES, UNIVERSITY_CHOICES, EVENT_TIME_CHOICES
from django.utils import timezone

# Create your models here.


class Customer(User):
    class Meta:
        ordering = ['first_name']
        verbose_name_plural = 'customer'

    user = models.OneToOneField(User, parent_link=True, related_name='customer', on_delete=models.CASCADE, default=None)
    profile_image = models.ImageField(upload_to='images/profile/', default='profile/gojo.png')

    def __str__(self):
        return self.username


class Event(models.Model):
    SINGLE_EVENT = 'single'
    MULTI_EVENT = 'multi'
    EVENT_TYPE_CHOICES = [
        (SINGLE_EVENT, 'single-event'),
        (MULTI_EVENT, 'multi-event'),
    ]
    name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timings = models.CharField(max_length=100)
    short_description = models.CharField(max_length=200)
    additional_info = models.TextField(blank=True)
    keywords = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        # Extract the time ranges from the string using regex
        matches = re.findall(r':\s+(\d{1,2}(?:am|pm)-\d{1,2}(?:am|pm))', self.timings)
        days = "Monday Tuesday Wednesday Thursday Friday Saturday Sunday"

        # print(self.name, matches)

        # Generate the times for each range
        times = []
        for match in matches:
            time_range = match
            start_time, end_time = time_range.split('-')
            start_time = datetime.datetime.strptime(start_time, "%I%p")
            end_time = datetime.datetime.strptime(end_time, "%I%p")
            curr_time = start_time
            while curr_time <= end_time:
                times.append(lower(curr_time.strftime("%I%p")))
                curr_time += datetime.timedelta(hours=1)
        times.append(days)
        times = set(times)
        # Join the list of times into a single string separated by space
        times_str = " ".join(times)

        # Split name, short_description, and additional_info fields into words
        words = []
        for field in [self.name, self.short_description, self.additional_info]:
            words += field.split()
        # Save the words as keywords
        self.keywords = ' '.join(set(words))
        self.keywords = self.keywords + ' ' + times_str
        super().save(*args, **kwargs)


class Ticket(models.Model):
    RESERVATION_CHOICES = [
        ('single-event', 'Single Event'),
        ('multi-event', 'Multi Event')
    ]
    reserved_event = models.ForeignKey(Event, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=12, choices=RESERVATION_CHOICES)
    reservation_date = models.DateField()
    reservation_time = models.CharField(max_length=12, choices=EVENT_TIME_CHOICES)
    is_student = models.BooleanField(default=False)
    university = models.CharField(max_length=50, choices=UNIVERSITY_CHOICES, default='University of Windsor')
    adult_tickets = models.IntegerField(default=0)
    children_tickets = models.IntegerField(default=0)
    total_price = models.DecimalField(max_digits=6, decimal_places=2)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100, choices=CITY_CHOICES)
    province = models.CharField(max_length=50, choices=PROVINCE_CHOICES)
    phone_number = models.CharField(max_length=10)
    ticket_id = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=50)
    transaction_timestamp = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return f"{self.reserved_event} - {self.ticket_id}"

