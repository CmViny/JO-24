from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        label='',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse e-mail'})
    )
    first_name = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'})
    )
    last_name = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de famille'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    field_attributes = {
        'username': {
            'placeholder': 'Nom d’utilisateur',
            'help_text': '<span class="form-text text-muted"><small>Obligatoire. 150 caractères ou moins. Lettres, chiffres et @/./+/-/_ uniquement.</small></span>'
        },
        'password1': {
            'placeholder': 'Mot de passe',
            'help_text': (
                "<ul class=\"form-text text-muted small\">"
                "<li>Votre mot de passe ne doit pas trop ressembler à vos autres informations personnelles.</li>"
                "<li>Il doit contenir au moins 8 caractères.</li>"
                "<li>Il ne peut pas être un mot de passe couramment utilisé.</li>"
                "<li>Il ne peut pas être uniquement numérique.</li>"
                "</ul>"
            )
        },
        'password2': {
            'placeholder': 'Confirmer le mot de passe',
            'help_text': '<span class="form-text text-muted"><small>Répétez le mot de passe pour vérification.</small></span>'
        }
    }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        for field, attrs in self.field_attributes.items():
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': attrs['placeholder']
            })
            self.fields[field].label = ''
            self.fields[field].help_text = attrs.get('help_text', '')

class UpdateProfileForm(forms.ModelForm):
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse e-mail'})
    )
    first_name = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'})
    )
    last_name = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de famille'})
    )
    age = forms.IntegerField(
        label='',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Âge'})
    )
    telephone = forms.CharField(
        label='',
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'})
    )
    adresse = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    field_attributes = {
        'username': {
            'placeholder': 'Nom d’utilisateur',
            'help_text': '<span class="form-text text-muted"><small>Obligatoire. 150 caractères ou moins. Lettres, chiffres et @/./+/-/_ uniquement.</small></span>'
        }
    }

    def __init__(self, *args, **kwargs):
        utilisateur_instance = kwargs.pop('utilisateur_instance', None)
        super().__init__(*args, **kwargs)

        # Champs User
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': self.field_attributes['username']['placeholder']
        })
        self.fields['username'].label = ''
        self.fields['username'].help_text = self.field_attributes['username']['help_text']

        # Pré-remplir les champs du modèle Utilisateur si instance fournie
        if utilisateur_instance:
            self.fields['age'].initial = utilisateur_instance.age
            self.fields['telephone'].initial = utilisateur_instance.telephone
            self.fields['adresse'].initial = utilisateur_instance.adresse

    def save(self, commit=True, utilisateur_instance=None):
        user = super().save(commit=commit)

        if utilisateur_instance:
            utilisateur_instance.age = self.cleaned_data.get('age')
            utilisateur_instance.telephone = self.cleaned_data.get('telephone')
            utilisateur_instance.adresse = self.cleaned_data.get('adresse')
            if commit:
                utilisateur_instance.save()

        return user

