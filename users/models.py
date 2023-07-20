from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for tutorial.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    #: First and last name do not cover name patterns around the globe
    point_balance = models.IntegerField(default=5000)
    stripe_customer_id=models.CharField(max_length=200, blank=True, null=True)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

class PointProducts(models.Model):
    points = models.IntegerField()
    price = models.PositiveIntegerField()

    def __str__(self):
        return str(self.price)
    
class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Subscription"

    # def activate(self):
    #     self.is_active = True
    #     self.save()

    # def deactivate(self):
    #     self.is_active = False
    #     self.end_date = None
    #     self.save()