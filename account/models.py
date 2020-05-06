import decimal

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import DecimalField
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class MyUser(AbstractUser):
    pass


class Balance(models.Model):
    INITIAL_BALANCE = 100

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='balance')
    usd = models.DecimalField(max_digits=10, decimal_places=2, default=INITIAL_BALANCE)
    rub = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    eur = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @receiver(post_save, sender=MyUser)  # FIXME
    def update_profile_signal(sender, instance, created, **kwargs):
        if created:
            Balance.objects.create(user=instance)
        instance.balance.save()

    def update_balance(self, currency: str, value: DecimalField):
        updated_currency = getattr(self, currency)
        updated_currency += decimal.Decimal(value)
        setattr(self, currency, updated_currency)
        self.save(update_fields=[currency])
        return self

    def __str__(self):
        return f'User: {self.user.username} - (USD:{self.usd}, RUB:{self.rub}, EUR:{self.eur})'


class Transfer(models.Model):
    CURRENCY = ('usd', 'rub', 'eur')
    CURSE = dict(zip(CURRENCY, [70, 1, 80]))
    COMMISSIONS = dict(zip(CURRENCY, [0.03, 0.05, 0.03]))

    sender = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='transfer', blank=True)
    created = models.DateField(auto_now_add=True, db_index=True, verbose_name=_('Date creation'))
    value = models.PositiveIntegerField(verbose_name=_('Value from currency'))
    senders_currency = models.CharField(
        default=None, blank=False, null=False, choices=((x, _(x)) for x in CURRENCY), max_length=5
    )
    payee_currency = models.CharField(
        default=None, blank=False, null=False, choices=((x, _(x)) for x in CURRENCY), max_length=5
    )
    payee = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='choices', blank=False)

    def conversion(self):
        coeff_commission = 0 if (self.sender == self.payee) else self.COMMISSIONS.get(self.senders_currency)
        if self.senders_currency != self.payee_currency:
            coeff_curse = self.CURSE[self.senders_currency]/self.CURSE[self.payee_currency]
        else:
            coeff_curse = 1

        sender_account = -(self.value + coeff_commission * self.value)
        payee_account = abs(self.value) * coeff_curse
        self.sender.balance.update_balance(currency=self.senders_currency, value=sender_account)
        self.payee.balance.update_balance(currency=self.payee_currency, value=payee_account)
