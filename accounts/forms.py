from django import forms

from .models import User, UserProfile
from .validators import allow_only_images_validator

class UserForm(forms.ModelForm):
  password = forms.CharField(widget=forms.PasswordInput())
  password_confirm = forms.CharField(widget=forms.PasswordInput())
  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'username', 'email', 'password', 'password_confirm']
  def clean(self):
    clean_data = super(UserForm, self).clean()
    password = clean_data.get('password')
    password_confirm = clean_data.get('password_confirm')
    if password_confirm != password:
      raise forms.ValidationError("Password did not match.")

class UserProfileForm(forms.ModelForm):
  profile_picture = forms.FileField(widget=forms.FileInput(
    attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])
  cover_photo = forms.FileField(widget=forms.FileInput(
    attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])
  # latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
  # longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
  address = forms.CharField(widget=forms.TextInput(
    attrs={'placeholder': 'Start typing ...', 'required': 'required'}))
  class Meta:
    model = UserProfile
    fields = ['profile_picture', 'cover_photo', 'address',
              'country', 'city', 'pin_code', 'latitude', 'longitude']
    
  def __init__(self, *args, **kwargs):
    super(UserProfileForm, self).__init__(*args, **kwargs)
    for field in self.fields:
      if field == 'latitude' or field == 'longitude':
        self.fields[field].widget.attrs['readonly'] = 'readonly'
    