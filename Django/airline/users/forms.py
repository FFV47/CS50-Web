from django import forms


class UserForm(forms.Form):
    username = forms.CharField(label="Username", max_length=20)
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput, help_text="Keep it safe!"
    )
