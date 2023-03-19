from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.urls import reverse
from django.contrib.auth import get_user_model

import os
import ast
# Create your models here.

User = get_user_model()


class Deck(models.Model):
    name = models.CharField(max_length=200)
    flashcards = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    csv = models.FileField(max_length=100, null=True, blank=True, upload_to='csv_files/')
    excl = models.FileField(max_length=100, null=True, blank=True, upload_to='xlsx_files/')
    anki = models.FileField(max_length=100, null=True, blank=True, upload_to='apkg_files/')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Deck_detail", kwargs={"pk": self.pk})
    
    def create_list_of_flashcards(self):
        l_cards = self.flashcards.replace(":", ",")
        list_from_string = ast.literal_eval(l_cards)
        return list_from_string
    
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





