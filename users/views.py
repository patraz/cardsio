from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView, TemplateView
from django.conf import settings
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from .models import PointProducts, Subscription
import datetime
import stripe
from django.contrib import messages


User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET



class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"



class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()

class CreateCheckoutSessionView(generic.View, LoginRequiredMixin):
    def post(self, request, *args, **kwargs):
        # plan = PointProducts.objects.get(price=kwargs["price"])
        price = kwargs["price"]
        if price == 499:
            domain = "https://flashio.co"
            session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price': 'price_1NZdSaEiQ1AZTnsDAkUMLRTG',
                        'quantity': 1,
                        
                    }
                ],
                mode='subscription',
                success_url=domain + reverse("success"),
                cancel_url=domain + reverse("user-decks"),
                metadata={
                    "user_email": request.user.email
                }
            )
        elif price == 799:
                    domain = "https://flashio.co"
                    session = stripe.checkout.Session.create(
                        line_items=[
                            {
                                'price': 'price_1NXOe9EiQ1AZTnsD83iqur8Q',
                                'quantity': 1,
                                
                            }
                        ],
                        mode='subscription',
                        success_url=domain + reverse("success"),
                        cancel_url=domain + reverse("user-decks"),
                        metadata={
                            "user_email": request.user.email
                        }
                    )
        return redirect(session.url, code=303)

class SuccessView(generic.TemplateView):
    template_name = "success.html"

class PricingView(generic.TemplateView):
    template_name = "flashcards/pricing.html"


def cancel_subscription(request):
    user = request.user
    subscription = Subscription.objects.get(user=user)
    sub_id = subscription.sub_id

    # Delete the subscription in Stripe
    
    try:
        response = stripe.Subscription.delete(sub_id)
        print(response)
        if response['status'] == 'canceled':
            # Subscription canceled successfully, delete the local subscription object
            subscription.delete()
            messages.warning(request, 'Subscription canceled')
        else:
            messages.error(request, 'Failed to cancel subscription. Please try again.')
    except stripe.error.StripeError as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect("users:detail", username=request.user.username)

@csrf_exempt
def stripe_webhook(request, *args, **kwargs):
    CHECKOUT_SESSION_COMPLETED = "checkout.session.completed"
    SUBSCRIPTION_SESSION_UPDATED = "customer.subscription.updated"
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print(e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(e)
        return HttpResponse(status=400)

    if event["type"] == CHECKOUT_SESSION_COMPLETED:
        # print(event)
        amount_total = event["data"]["object"]["amount_total"]
        user_email = event["data"]["object"]["metadata"]["user_email"]
        subscription = event["data"]["object"]["subscription"]
        #Add balance
        sub = stripe.Subscription.retrieve(
        subscription
        )
        user = User.objects.get(email=user_email)
        has_subscription = Subscription.objects.filter(user=user).exists()
        if has_subscription is False:
            Subscription.objects.create(user=user, start_date=datetime.datetime.fromtimestamp(sub["current_period_start"]),
                                        end_date=datetime.datetime.fromtimestamp(sub["current_period_end"]),
                                        sub_id = subscription,
                                        is_active = True)
        # print('user',user)
        print(amount_total)
        if amount_total == 799:
            user.point_balance = user.point_balance + 200000
            user.save()
        elif amount_total == 499:
            user.point_balance = user.point_balance + 50000
            user.save()
    return HttpResponse()


