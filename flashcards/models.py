from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_init
from django.urls import reverse
from django.contrib.auth import get_user_model

import os
import ast

from flashcards.utils import create_apkg_from_csv, create_csv, create_xlsx
# Create your models here.

User = get_user_model()



class Deck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    list = models.TextField()
    csv = models.FileField(max_length=100, null=True, blank=True, upload_to='csv_files/')
    excl = models.FileField(max_length=100, null=True, blank=True, upload_to='xlsx_files/')
    anki = models.FileField(max_length=100, null=True, blank=True, upload_to='apkg_files/')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Deck_detail", kwargs={"pk": self.pk})
    
    def cost(self):
        flashcards = self.flashcard_set.count()
        return flashcards *120
    
class Flashcard(models.Model):
    deck = models.ForeignKey(Deck,  on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()

@receiver(post_delete, sender=Deck)
def delete_deck_files(sender, instance, **kwargs):
    """
    Deletes associated CSV, EXCL, and Anki files when a Deck instance is deleted.
    """
    # Delete CSV file
    if instance.csv:
        try:
            os.remove(instance.csv.path)
        except Exception as e:
            # Code to handle the exception
            print("An error occurred:", e)

    if instance.excl:
        try:
            os.remove(instance.excl.path)
        except Exception as e:
            # Code to handle the exception
            print("An error occurred:", e)

    if instance.anki:
        try:
            os.remove(instance.anki.path)
        except Exception as e:
            # Code to handle the exception
            print("An error occurred:", e)


@receiver(post_init, sender=Deck)
def create_deck_files(sender, instance, **kwargs):
    create_xlsx(list(instance.list), instance.pk)
    create_csv(list(instance.list), instance.pk)
    create_apkg_from_csv(list(instance.list),instance.pk)
    xlsx_file=f"./xlsx_files/{instance.pk}.xlsx"
    csv_file = f"./csv_files/{instance.pk}.csv"
    apkg_file = f"./apkg_files/{instance.pk}.apkg"
    instance.excl = xlsx_file
    instance.csv = csv_file
    instance.anki = apkg_file
    instance.save()       

