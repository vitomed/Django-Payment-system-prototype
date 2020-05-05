from django import forms

from account.models import MyUser, Balance, Transfer


class UserForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ('username',)


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('username',)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            return username
        raise forms.ValidationError('This username is already exist.')


class BalanceForm(forms.ModelForm):
    class Meta:
        model = Balance
        fields = ('usd', 'rub', 'eur')


class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ('user_to', 'currency_from', 'currency_to', 'value')