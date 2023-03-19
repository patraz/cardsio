from django import forms

class FlashcarForm(forms.Form):

     


    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('pl', 'Polish'),
    )

     
    prompt = forms.CharField(label='What it the topic you want flashcards to have?', max_length=200)
    amount = forms.IntegerField(label='What amount of flashcards would you like to create?', min_value=5, max_value=20)
    language = forms.ChoiceField(label='Which language you want your flashcards to be in?', choices=LANGUAGE_CHOICES)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request") # store value of request 
        print(self.request.user) 
        super().__init__(*args, **kwargs)

    def clean_amount(self, *args, **kwargs):
        print(self, *args, **kwargs)
        user = self.request.user
        amount = self.cleaned_data.get('amount')
        point_cost = amount*120
        if user.point_balance < point_cost:
            raise forms.ValidationError(f"You don't have enough points to make this request. Your balance is {user.point_balance}, and cost of this request is {point_cost}")
        return amount

    