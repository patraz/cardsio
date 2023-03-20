import os
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from .forms import FlashcarForm, FlashcardTextForm
from .models import Deck, Flashcard
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.contrib.auth import get_user_model
from django.conf import settings
from .utils import create_csv, create_xlsx, create_apkg_from_csv, create_flashcards
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
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": f"""
                        Create a list of {amount} flashcards in {language} from this text: {text}.
                        Do not use quotations in questions and answers, only provide a  Python list compliant response  following this format without deviation. 
                        [
                        ["Question":"Answer"],
                        ]"""}],
                    temperature=0,
                    max_tokens=2048,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                    )
                print(response["choices"][0]["message"].content)
                request.user.point_balance = request.user.point_balance - amount*120
                request.user.save()
                resp = response["choices"][0]["message"].content
                d_old_str = resp.replace('\n', '') # remove all \n
                if d_old_str[-1] != ']':
                    d_old_str = d_old_str + '"]]'

                

                deck = Deck.objects.create(name = subject, list=d_old_str, user=request.user)
                
                f_cards = deck.create_list_of_flashcards()
                create_xlsx(f_cards, deck.pk)
                create_csv(f_cards, deck.pk)
                create_apkg_from_csv(deck.pk)
                xlsx_file=f"./xlsx_files/{deck.pk}.xlsx"
                csv_file = f"./csv_files/{deck.pk}.csv"
                apkg_file = f"./apkg_files/{deck.pk}.apkg"
                deck.excl = xlsx_file
                deck.csv = csv_file
                deck.anki = apkg_file
                deck.save()

                pack = create_flashcards(d_old_str)
                for x in pack:
                    Flashcard.objects.create(question=x[0], answer=x[1], deck=deck)

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
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    # prompt=f"""
                    #     Create a list of {amount} flashcards in {language} about {user_prompt}.
                    #     Do not include any explanations, do not use quotations in questions and answers only provide a  Python list compliant response  following this format without deviation. 
                    #     [
                    #     ['Question': 'string', 'Answer': 'string'],
                    #     ]""",
                    messages=[{"role": "user", "content": f"""
                        Create a list of {amount} flashcards in {language} about {user_prompt}.
                        Do not use quotations in questions and answers, only provide a  Python list compliant response  following this format without deviation. 
                        [
                        ["Question":"Answer"],
                        ]"""}],
                    temperature=0,
                    max_tokens=2048,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                    )
                print(language)
                print(response["choices"][0]["message"].content)
                request.user.point_balance = request.user.point_balance - amount*120
                request.user.save()
                resp = response["choices"][0]["message"].content
                d_old_str = resp.replace('\n', '') # remove all \n
                if d_old_str[-1] != ']':
                    d_old_str = d_old_str + '"]]'

                

                deck = Deck.objects.create(name = user_prompt, list=d_old_str, user=request.user)
                
                f_cards = deck.create_list_of_flashcards()
                create_xlsx(f_cards, deck.pk)
                create_csv(f_cards, deck.pk)
                create_apkg_from_csv(deck.pk)
                xlsx_file=f"./xlsx_files/{deck.pk}.xlsx"
                csv_file = f"./csv_files/{deck.pk}.csv"
                apkg_file = f"./apkg_files/{deck.pk}.apkg"
                deck.excl = xlsx_file
                deck.csv = csv_file
                deck.anki = apkg_file
                deck.save()

                pack = create_flashcards(d_old_str)
                for x in pack:
                    Flashcard.objects.create(question=x[0], answer=x[1], deck=deck)

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
        return Deck.objects.get_queryset().order_by('id')

class UserDecksListView(generic.ListView):
    template_name = "decks.html"
    context_object_name = 'decks'
    paginate_by=10
    def get_queryset(self):
        return Deck.objects.filter(user=self.request.user)

class DeckDetailView(generic.ListView):
    template_name = "detail.html"
    paginate_by=10
    


    context_object_name = 'flashcards'


    def get_queryset(self,*args, **kwargs):
        deck = Deck.objects.get(pk=self.kwargs["pk"])
        return Flashcard.objects.filter(deck=deck)
    def get_context_data(self, **kwargs):
        context = super(DeckDetailView, self).get_context_data(**kwargs)
        
        deck = Deck.objects.get(pk=self.kwargs["pk"])

        f_cards = deck.create_list_of_flashcards()

        context.update({
            'object':deck,
            'f_list':[f_cards]
        })
        return context
    
class DeckDeleteView(generic.DeleteView):
    model = Deck
    success_url = reverse_lazy('user-decks') # replace 'myapp:index' with the URL name of your view
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Object deleted successfully.')
        return super().delete(request, *args, **kwargs)


class CsvDownloadView(generic.View):
    def get(self, request, *args, **kwargs):
        deck = Deck.objects.get(pk=kwargs['pk'])
        filename = os.path.basename(deck.csv.name)
        response = HttpResponse(deck.csv, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
    
class XlsxDownloadView(generic.View):
    def get(self, request, *args, **kwargs):
        deck = Deck.objects.get(pk=kwargs['pk'])
        filename = os.path.basename(deck.excl.name)
        response = HttpResponse(deck.excl, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
    

def download_file(filetype, kwargs):
    deck = Deck.objects.get(pk=kwargs['pk'])
    filename = os.path.basename(deck.filetype.name)
    response = HttpResponse(deck.filetype, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response

    
class ApkgDownloadView(generic.View):
    def get(self, request, *args, **kwargs):
        deck = Deck.objects.get(pk=kwargs['pk'])
        filename = os.path.basename(deck.anki.name)
        response = HttpResponse(deck.anki, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
    
