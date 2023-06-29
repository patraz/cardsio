import os

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from django.views import generic
from django.contrib.auth import get_user_model
from django.conf import settings

from flashcards.utils import create_apkg_from_csv, create_csv, create_xlsx

from .forms import FlashcarForm, FlashcardTextForm
from .models import Deck, Flashcard
from .tasks import get_flashcards_from_prompt, get_flashcards_from_text

from allauth.account.decorators import verified_email_required

import openai

openai.api_key = settings.OPENAI_KEY 
User = get_user_model()


@verified_email_required
def form_text(request):
    if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = FlashcardTextForm(request.POST, request = request)
            # check whether it's valid:
            if form.is_valid():
                subject = form.cleaned_data['subject']
                text = form.cleaned_data['text']
                language = form.cleaned_data['language']
                amount = form.cleaned_data['amount']
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:

                get_flashcards_from_text.delay(amount=amount, language=language, subject=subject, text=text, email=request.user.email)

                messages.success(request, 'Creating flashcards can take a while, you will get an e-mail when they are done :)')
                return redirect("user-decks")

        # if a GET (or any other method) we'll create a blank form
    else:
            form = FlashcardTextForm(request =  request)

    context = {
          'form': form,

    }
    return render(request, 'text_form.html', context)


# Create your views here.
@verified_email_required
def form(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = FlashcarForm(request.POST, request = request)
        # check whether it's valid:
        if form.is_valid():
            user_prompt = form.cleaned_data['prompt']
            amount = form.cleaned_data['amount']
            language = form.cleaned_data['language']
            get_flashcards_from_prompt.delay(amount=amount, language=language, user_prompt=user_prompt, email=request.user.email)

            messages.success(request, 'Creating flashcards can take a while, refresh your decks later')
            return redirect("user-decks")

        # if a GET (or any other method) we'll create a blank form
    else:
            form = FlashcarForm(request =  request)

    context = {
          'form': form,

    }

    return render(request, 'form.html', context)

class DecksListView(generic.ListView):
    template_name = "alldecks.html"
    context_object_name = 'decks'
    paginate_by=10
    def get_queryset(self):
        qs = Deck.objects.get_queryset()
        title = self.request.GET.get('title', None)
        if title:
            qs = qs.filter(name__icontains=title)
        return qs.order_by('-id')


class UserDecksListView(generic.ListView):
    template_name = "decks.html"
    context_object_name = 'decks'
    paginate_by=10
    def get_queryset(self):
        qs = Deck.objects.filter(user=self.request.user)
        title = self.request.GET.get('title', None)
        if title:
            qs = qs.filter(name__icontains=title)
        return qs.order_by('-id')

class DeckDetailView(generic.ListView):
    template_name = "detail.html"
    paginate_by=12
    context_object_name = 'flashcards'


    def get_queryset(self,*args, **kwargs):
        deck = Deck.objects.get(pk=self.kwargs["pk"])
        return Flashcard.objects.filter(deck=deck)
    
    def get_context_data(self, **kwargs):
        context = super(DeckDetailView, self).get_context_data(**kwargs)
        deck = Deck.objects.get(pk=self.kwargs["pk"])
        flashcards = deck.flashcard_set.count()
        context.update({
            'object':deck,
            'f_count':flashcards
        })
        return context
    
class DeckDeleteView(generic.DeleteView):
    model = Deck
    success_url = reverse_lazy('user-decks') # 
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Object deleted successfully.')
        return super().delete(request, *args, **kwargs)


class CsvDownloadView(generic.View):
    def get(self, request, *args, **kwargs):
        deck = Deck.objects.get(pk=kwargs['pk'])
        create_csv(deck.list, deck.pk)
        csv_file = f"./csv_files/{deck.pk}.csv"
        deck.csv = csv_file
        deck.save()
        filename = os.path.basename(deck.csv.name)
        response = HttpResponse(deck.csv, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
    
class XlsxDownloadView(generic.View):
    def get(self, request, *args, **kwargs):
        deck = Deck.objects.get(pk=kwargs['pk'])
        create_xlsx(deck.list, deck.pk)
        xlsx_file=f"./xlsx_files/{deck.pk}.xlsx"
        deck.excl = xlsx_file
        deck.save()
        filename = os.path.basename(deck.excl.name)
        response = HttpResponse(deck.excl, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
    
    
class ApkgDownloadView(generic.View):
    def get(self, request, *args, **kwargs):
        deck = Deck.objects.get(pk=kwargs['pk'])
        try:
            create_apkg_from_csv(deck.pk)
            apkg_file = f"./apkg_files/{deck.pk}.apkg"
            deck.anki = apkg_file
            deck.save()
        except FileNotFoundError:
            create_csv(deck.list, deck.pk)
            csv_file = f"./csv_files/{deck.pk}.csv"
            deck.csv = csv_file
            create_apkg_from_csv(deck.pk)
            apkg_file = f"./apkg_files/{deck.pk}.apkg"
            deck.anki = apkg_file
            deck.save()
        except ValueError:
            print("Value Error")

        filename = os.path.basename(deck.anki.name)
        response = HttpResponse(deck.anki, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
    
