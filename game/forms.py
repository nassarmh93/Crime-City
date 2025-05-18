from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # Use Django's default User model
from game.models import Player

class RegistrationForm(UserCreationForm):
    """
    Form for user registration with additional fields
    """
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
        return user

class PlayerProfileForm(forms.ModelForm):
    """
    Form for editing player profile
    """
    class Meta:
        model = Player
        fields = ('nickname',)
        
    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        # Check if nickname already exists for another player
        if Player.objects.filter(nickname=nickname).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("This nickname is already taken. Please choose another one.")
        return nickname 