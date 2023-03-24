import os
from celery import shared_task

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse

from .utils import create_list_of_flashcards
from .models import Deck, Flashcard

import openai

User = get_user_model()

from_email = settings.DEFAULT_FROM_EMAIL
subject = '[Flashio] Your flashcards are ready'


openai.api_key = settings.OPENAI_KEY 

@shared_task
def get_flashcards_from_prompt(amount, language, user_prompt, email):
    user = User.objects.get(email=email)
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert that creates flashcards anout given topic"},
            {"role": "user", "content": f"""
            Create a list of {amount} flashcards in {language} about {user_prompt}.
            Only provide a  Python list compliant response  following this format without deviation. 
            [
            ["Question":"Answer"],
            ]"""}],
        temperature=0,
        max_tokens=3877,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    print(user.point_balance)
    user.point_balance = user.point_balance - amount*120
    user.save()
    resp = response["choices"][0]["message"].content

    d_old_str = resp.replace('”','').replace('„','') # remove all \n


    try:
        f_cards = create_list_of_flashcards(d_old_str)
    except:
        last_bracket_index = d_old_str.rfind(']')
        x = d_old_str[:last_bracket_index+1] + ']'
        f_cards = create_list_of_flashcards(x)


    deck = Deck.objects.create(name = user_prompt, list=f_cards, user=user)

    for x in f_cards:
                Flashcard.objects.create(question=x[0], answer=x[1], deck=deck)
    recipient_list = [f'{email}']
    message = f'Flashio generated {len(f_cards)} flashcards about {user_prompt}, check them at your dashboard'
    send_mail(subject, message, from_email, recipient_list)
    return

@shared_task
def get_flashcards_from_text(subject, text, language, amount, email):
    user = User.objects.get(email=email)
    text = text.replace('\n', '').replace('”','').replace('„','').replace("''", "").replace('""','')
    if language == 'Polish':
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Jesteś pomocnym asystentem i expertem, który tworzy flashcards na dany temat"},
            {"role": "user", "content": f"""
            Stwórz listę {amount} flashcards w języku {language} z tego tekstu: {text}.
            Do not use quotations in questions and answers, only provide a  Python list compliant response  following this format without deviation. 
            [["Pytanie":"Odpowiedź"],]"""}],
        temperature=0,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    else:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert that creates flashcards anout given topic"},
            {"role": "user", "content": f"""
            Create a list of {amount} flashcards in {language} from this text: {text}.
            Do not use quotations in questions and answers, only provide a  Python list compliant response  following this format without deviation. 
            [["Question":"Answer"]]"""}],
        temperature=0,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    print(response["choices"][0]["message"].content)
    user.point_balance = user.point_balance - amount*120
    user.save()
    resp = response["choices"][0]["message"].content
    
    d_old_str = resp.replace('\n', '').replace('”','').replace('„','') # remove all \n

    try:
        f_cards = create_list_of_flashcards(d_old_str)
    except:
        last_bracket_index = d_old_str.rfind(']')
        x = d_old_str[:last_bracket_index+1] + ']'
        f_cards = create_list_of_flashcards(x)

    deck = Deck.objects.create(name = subject, list=f_cards, user=user)

    for x in f_cards:
                Flashcard.objects.create(question=x[0], answer=x[1], deck=deck)
    recipient_list = [f'{email}']
    message = f'Flashio generated {len(f_cards)} flashcards about {subject}, check them at your dashboard'
    send_mail(subject, message, from_email, recipient_list)
    return       

