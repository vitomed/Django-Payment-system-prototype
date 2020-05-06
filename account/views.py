from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views import View
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin

from account.forms import RegistrationForm, BalanceForm, TransferForm


@login_required
def account(request):
    balance_form = BalanceForm(instance=request.user.balance)
    context = {'balance_form': balance_form, 'section': 'account'}
    return render(request, 'account/account.html', context=context)


class TransferView(LoginRequiredMixin, View):

    _transfer_form = TransferForm

    def get(self, request):
        transfer_form = TransferForm()
        context = {'transfer_form': transfer_form, 'section': 'transfer'}
        return render(request, 'account/transfer.html', context=context)

    @transaction.atomic
    def post(self, request):
        transfer_form = self._transfer_form(data=request.POST)
        sender = request.user
        if transfer_form.is_valid():
            new_transfer = transfer_form.save(commit=False)
            new_transfer.sender = getattr(sender, '_wrapped')
            new_transfer.save()
            new_transfer.conversion()
            messages.info(request, f'Transfer to "{new_transfer.payee.get_username()}", successfully completed!')
            return redirect('/account/')


class Register(View):
    _user_form = RegistrationForm
    _template_register = 'account/register.html'
    _template_done = 'account/register_done.html'

    def get(self, request):
        user_form = self._user_form()
        context = {'user_form': user_form}
        return render(request, self._template_register, context=context)

    @transaction.atomic
    def post(self, request):
        user_form = self._user_form(request.POST)

        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.username = user_form.cleaned_data['username']
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            context = {'new_user': new_user}
            return render(request, self._template_done, context=context)  # FIXME

        messages.error(request, f'User with name "{user_form.data.get("username")}", already exist!')
        return redirect('/account/register/')
