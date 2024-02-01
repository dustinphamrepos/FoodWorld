from django import forms

from .models import User

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
    