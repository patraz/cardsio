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
from .models import PointProducts
import datetime
import stripe


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
        plan = PointProducts.objects.get(price=kwargs["price"])


        domain = "https://flashio.co"
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    # 'price_data': {
                    #     'currency': 'usd',
                    #     'product_data': {
                    #         'name': f'{plan.points} points',
                    #     },
                    #     'unit_amount': plan.price,
                    # },
                    'price': 'price_1NVwrBEiQ1AZTnsD46E4xKbE',
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
        # print('amount', amount_total, 'user_email:', user_email)
        #Add balance
        user = User.objects.get(email=user_email)
        # print('user',user)
        if amount_total == 1500:
            user.point_balance = user.point_balance + 200000
            user.save()
    if event["type"] == SUBSCRIPTION_SESSION_UPDATED:
        print('user', user_email)
        
        current_end_date = event["data"]["object"]["current_period_end"]
        # user = User.objects.get(email=user_email)
        # print(user)
        # user.subscription.start_date = datetime.datetime.now()
        # user.subscription.end_date = datetime.datetime.fromtimestamp(current_end_date)
        # user.save()
    return HttpResponse()


