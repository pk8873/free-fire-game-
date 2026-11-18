from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from players.models import PlayerProfile, Team
from tournaments.models import MatchDispute

class SignUpForm(UserCreationForm):
    email=forms.EmailField(required=True)
    in_game_name=forms.CharField(max_length=40)
    game_uid=forms.CharField(max_length=32,label='Game UID')
    phone=forms.CharField(max_length=20,required=False)
    class Meta:
        model=User
        fields=('username','email','in_game_name','game_uid','phone','password1','password2')
    def clean_game_uid(self):
        value=self.cleaned_data['game_uid'].strip()
        if PlayerProfile.objects.filter(game_uid__iexact=value).exists():
            raise forms.ValidationError('This Game UID is already registered.')
        return value
    def save(self, commit=True):
        from django.db import transaction
        if not commit:
            return super().save(commit=False)
        with transaction.atomic():
            user=super().save(commit=True)
            user.email=self.cleaned_data['email'].strip()
            user.save(update_fields=['email'])
            PlayerProfile.objects.create(user=user,game_uid=self.cleaned_data['game_uid'].strip(),in_game_name=self.cleaned_data['in_game_name'].strip(),phone=self.cleaned_data.get('phone','').strip())
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model=PlayerProfile
        fields=('in_game_name','game_uid','phone')
    def clean_game_uid(self):
        value=self.cleaned_data['game_uid'].strip()
        if PlayerProfile.objects.filter(game_uid__iexact=value).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This Game UID is already registered.')
        return value

class TeamCreateForm(forms.ModelForm):
    class Meta:
        model=Team
        fields=('name',)
        widgets={'name':forms.TextInput(attrs={'placeholder':'Your squad name'})}

class JoinTeamForm(forms.Form):
    join_code=forms.CharField(max_length=8,label='Team invite code')

class DisputeForm(forms.ModelForm):
    class Meta:
        model=MatchDispute
        fields=('message',)
        widgets={'message':forms.Textarea(attrs={'rows':4,'placeholder':'Explain the issue clearly. Do not include passwords or private data.'})}

class MatchResultForm(forms.Form):
    score_a=forms.IntegerField(min_value=0,max_value=99,label='Team A score')
    score_b=forms.IntegerField(min_value=0,max_value=99,label='Team B score')
