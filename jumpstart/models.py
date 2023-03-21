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

