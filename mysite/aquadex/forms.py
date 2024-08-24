from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
from django import forms

class CreateUserForm(UserCreationForm): 
     password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control input-field', 'placeholder': 'Password'}))
     password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control input-field', 'placeholder': 'Re-enter Password'}))
     class Meta:
        model = User 
        fields = ["username", "email", "password1", "password2"] 
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control input-field', 'placeholder': 'Username'}),  
                   'email': forms.EmailInput(attrs={'class': 'form-control input-field', 'placeholder': 'Email'}),}  

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  
         
        self.fields['old_password'].widget.attrs.update({'class': 'old_password'})  
        self.fields['new_password1'].widget.attrs.update({'class': 'new_password1'})  
        self.fields['new_password2'].widget.attrs.update({'class': 'new_password2'})  
