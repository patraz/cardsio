from django import forms

class FlashcarForm(forms.Form):
    LANGUAGE_CHOICES = (
        ('English', 'English'),
        ('Polish', 'Polish'),
        ('Japanese', 'Japanese'),
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

class FlashcardTextForm(forms.Form):
    LANGUAGE_CHOICES = (
        ('English', 'English'),
        ('Polish', 'Polish'),
        ('Japanese', 'Japanese'),
    )

    
    subject = forms.CharField(label='Whats the subject of your text?', max_length=100)
    text = forms.CharField(label='Your Text', widget=forms.Textarea, max_length=5000)
    language = forms.ChoiceField(label='Which language you want your flashcards to be in?', choices=LANGUAGE_CHOICES)
    amount = forms.IntegerField(label='What amount of flashcards would you like to create?', min_value=5, max_value=30)

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