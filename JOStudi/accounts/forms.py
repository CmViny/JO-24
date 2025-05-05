from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class SignUpForm(UserCreationForm):
    # Définition explicite des champs pour les formulaires
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    first_name = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    field_attributes = {
        'username': {'placeholder': 'User Name', 'help_text': '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'},
        'password1': {'placeholder': 'Password', 'help_text': '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'},
        'password2': {'placeholder': 'Confirm Password', 'help_text': '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'}
    }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        # Appliquer uniquement les attributs pour les champs qui ne sont pas définis explicitement
        for field, attrs in self.field_attributes.items():
            self.fields[field].widget.attrs.update({'class': 'form-control', 'placeholder': attrs['placeholder']})
            self.fields[field].label = attrs.get('label', '')  # Si pas de label, met une chaîne vide
            self.fields[field].help_text = attrs.get('help_text', '')
