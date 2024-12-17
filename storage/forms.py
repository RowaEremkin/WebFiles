from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label='Username', max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Password',max_length=60, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Password repeat',max_length=60, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        t = kwargs.pop('t', None)
        super().__init__(*args, **kwargs)
        if(t != None):
            self.fields['email'].label = t['email']
            self.fields['username'].label = t['username']
            self.fields['password1'].label = t['password']
            self.fields['password2'].label = t['passwordRepeat']
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', max_length=60, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        t = kwargs.pop('t', None)
        super().__init__(*args, **kwargs)
        if(t != None):
            self.fields['username'].label = t['username']
            self.fields['password'].label = t['password']