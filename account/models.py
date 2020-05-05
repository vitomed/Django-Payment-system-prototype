from typing import Dict

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import DecimalField
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from functools import lru_cache
import decimal


class MyUser(AbstractUser):
    pass


class Balance(models.Model):
    INITIAL_BALANCE = 100
    PORTFOLIO = {x: x for x in ('usd', 'rub', 'eur')}  # TODO

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='balance')
    usd = models.DecimalField(max_digits=10, decimal_places=2, default=INITIAL_BALANCE)
    rub = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    eur = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @receiver(post_save, sender=MyUser)  # FIXME
    def update_profile_signal(sender, instance, created, **kwargs):
        if created:
            Balance.objects.create(user=instance)
        instance.balance.save()

    def update(self, currency: str, value: DecimalField):  # TODO
        PORTFOLIO: Dict[str, DecimalField] = {'USD': self.usd, 'RUB': self.rub, 'EUR': self.eur}
        PORTFOLIO[currency] += decimal.Decimal(value)
        return self

    def __str__(self):
        return f'User: {self.user.username} - (USD:{self.usd}, RUB:{self.rub}, EUR:{self.eur})'


class Transfer(models.Model):
    CURRENCY = ('USD', 'RUB', 'EUR')
    CURSE = dict(zip(CURRENCY, [70, 1, 80]))
    COMMISSIONS = dict(zip(CURRENCY, [0.08, 0.5, 0.04]))

    user = models.ForeignKey(
        MyUser, verbose_name=_('Transfer currency'), on_delete=models.CASCADE, related_name='transfer', blank=True
    )
    created = models.DateField(auto_now_add=True, db_index=True)
    value = models.PositiveIntegerField(verbose_name='Value from currency',)
    currency_from = models.CharField(default=None, blank=False, null=False, choices=((x, _(x)) for x in CURRENCY), max_length=5)
    currency_to = models.CharField(default=None, blank=False, null=False, choices=((x, _(x)) for x in CURRENCY), max_length=5)
    user_to = models.ForeignKey(MyUser, blank=False, on_delete=models.CASCADE, related_name='choices')

    @lru_cache(maxsize=1)
    def conversion(self):
        coeff_commission = 1 if (self is self.user) else self.COMMISSIONS.get(self.currency_from)
        if self.currency_from != self.currency_to:
            coeff_curse = self.CURSE[self.currency_from]/self.CURSE[self.currency_to]
        else:
            coeff_curse = 1

        subtraction = -self.value
        addition = coeff_commission * coeff_curse * self.value
        self.user.balance.update(currency=self.currency_from, value=subtraction)
        self.user_to.balance.update(currency=self.currency_to, value=addition)