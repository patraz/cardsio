"""flashio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.conf.urls.static import static
from django.views import generic

from flashcards.views import form, UserDecksListView, DeckDetailView, DeckDeleteView, CsvDownloadView, XlsxDownloadView, ApkgDownloadView
from users.views import SuccessView, PricingView, CreateCheckoutSessionView, stripe_webhook, admin_create, migrate, makemigrations



urlpatterns = [
    path("", generic.TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path('admin/', admin.site.urls),
    path("create-admin/", admin_create, name="admin-create"),
    path("migrate/", admin_create, name="migrate"),
    path("makemigrations/", admin_create, name="makemigrations"),
    path("form/", form, name="form"),
    path("decks/", UserDecksListView.as_view(), name="user-decks"),
    path('decks/<int:pk>/', DeckDetailView.as_view(), name='deck-detail'),
    path('decks/delete/<int:pk>', DeckDeleteView.as_view(), name='deck-delete'),
    path("decks/download-csv/<int:pk>", CsvDownloadView.as_view(), name="csv-download"),
    path("decks/download-xlsx/<int:pk>", XlsxDownloadView.as_view(), name="xlsx-download"),
    path("decks/download-apkg/<int:pk>", ApkgDownloadView.as_view(), name="apkg-download"),
    path("success/", SuccessView.as_view(), name="success"),
    path("pricing/", PricingView.as_view(), name="pricing"),
    path("checkout/<int:price>/", CreateCheckoutSessionView.as_view(), name="checkout"),
    path("stripe/webhook/", stripe_webhook, name="stripe-webhook"),
    # Django Admin, use {% url 'admin:index' %}
    # User management
    path("users/", include("users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]


