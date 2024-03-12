from django.contrib.auth.models import AbstractUser
from dateutil.relativedelta import relativedelta
from colorfield.fields import ColorField
from datetime import timedelta, date
from django.db.models import Sum, F
from django.urls import reverse
from django.db import models
from decimal import Decimal
import math


class CustomUser(AbstractUser):
    name = models.CharField(
        default="Your Name", max_length=100, null=False, blank=False
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        help_text="Used to extrapolate your age for " "calculations in the future.",
    )
    starting_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="A value to start the calculations with, like a checking "
        "account balance.",
    )
    accent_color = ColorField(
        default="#9400d3", help_text="Used throughout the app's UI."
    )
    dark_mode = models.BooleanField(default=True)
    toggle_raise = models.BooleanField(
        default=False,
        help_text="Toggle to use your raise percentage in income "
        "calculations after the first year.",
    )
    raise_pct = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal(1.03),
        verbose_name="Raise Percentage",
    )

    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        related_name="custom_user_set",  # Add this line
        related_query_name="custom_user",  # Add this line
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="custom_user_set",  # Add this line
        related_query_name="custom_user",  # Add this line
    )

    class Meta:
        verbose_name_plural = "User"

    def get_short_name(self):
        return self.name

    def get_admin_url(self):
        app, model = (self._meta.app_label, self._meta.model_name)
        return reverse("admin:{}_{}_change".format(app, model), args=(self.pk,))

    def get_current_age(self):
        return math.floor((date.today() - self.birth_date).days / 365)

    def get_years_old_from_num_months(self, num_months):
        new_date = date.today() + relativedelta(months=num_months)
        new_delta = new_date - self.birth_date
        return math.floor(new_delta.days / 365)

    def get_transactions(self, transaction_type):
        return (
            MonthlyTransaction.objects.filter(user=self, type=transaction_type)
            .annotate(total=Sum(F("multiplier") * F("amount")))
            .order_by("-total")
            .all()
        )

    def get_transactions_by_group(self, transaction_type):
        transactions_grouped = {}

        transactions = self.get_transactions(transaction_type)
        for transaction in transactions:
            group = transaction.group
            if group not in transactions_grouped:
                transactions_grouped[group] = {
                    "transactions": [transaction],
                    "group_total": group.total(),
                }
            else:
                transactions_grouped[group]["transactions"].append(transaction)

        return transactions_grouped

    def get_income_by_group(self):
        return self.get_transactions_by_group("in")

    def get_expenses_by_group(self):
        return self.get_transactions_by_group("ex")

    def get_investments_total(self):
        investments = (
            self.get_transactions("ex")
            .filter(group__group_name="Investment", muted__exact=False)
            .all()
        )
        return investments.aggregate(Sum("amount"))["amount__sum"]

    def get_paychecks_total(self):
        paycheck_group = TransactionGroup.objects.get(group_name="Employment")
        paychecks = self.get_transactions_by_group("in")[paycheck_group]
        return paychecks["group_total"]

    def get_monthly_transaction_total(self, transaction_type):
        monthly_total = Decimal(0.0)
        all_transactions = self.get_transactions(transaction_type)

        for transaction in all_transactions:
            if not transaction.muted:
                monthly_total += transaction.amount * transaction.multiplier
        return monthly_total

    def get_monthly_income_without_paycheck(self):
        monthly_income = self.get_monthly_transaction_total("in")
        paycheck_total = self.get_paychecks_total()
        return monthly_income - paycheck_total

    def get_income_calculations(self, years_to_project=1):
        total_monthly_income = self.get_monthly_transaction_total("in")
        total_monthly_expenses = self.get_monthly_transaction_total("ex")
        net_monthly_income = total_monthly_income - total_monthly_expenses

        net_monthly_income_with_raise = net_monthly_income
        if self.toggle_raise:
            paycheck_total = self.get_paychecks_total()
            income_without_paycheck = total_monthly_income - paycheck_total
            for year in range(2, years_to_project + 1):
                paycheck_total *= self.raise_pct
                net_monthly_income_with_raise = (
                    income_without_paycheck + paycheck_total
                ) - total_monthly_expenses

        return {
            "total_monthly_income": total_monthly_income,
            "total_monthly_expenses": total_monthly_expenses,
            "net_monthly_income": net_monthly_income,
            "net_monthly_income_with_raise": net_monthly_income_with_raise,
        }

    def get_net_income_calculations(self, years_to_project=1):
        years_to_project = int(years_to_project)
        now = date.today()
        total_months = years_to_project * 12
        step = int(years_to_project / 1)
        months = range(0, total_months + 1, step)
        income_calcs = self.get_income_calculations(years_to_project)
        total_monthly_investment = self.get_investments_total()

        net_income_calculations = []
        for month in months:
            new_date = now + timedelta(month * 365 / 12)
            date_string = new_date.strftime("%b %d, %Y")
            net_income = income_calcs["net_monthly_income"] * month
            new_total = self.starting_value + net_income
            new_age = self.get_years_old_from_num_months(num_months=month)
            investment = (
                (total_monthly_investment * month) if total_monthly_investment else 0.0
            )

            years_rounded = round(month / 12, 2)
            years_plural = "s" if years_rounded != 1.00 else ""
            years_string = "{:.2g} year{}".format(years_rounded, years_plural)

            raise_applies_to_date = new_date.year > now.year
            if self.toggle_raise and raise_applies_to_date:
                net_income_with_raise = net_income
                net_income = math.floor(net_income_with_raise * self.raise_pct)
                new_total = math.floor(new_total * self.raise_pct)

            months_plural = "s" if month != 1 else ""
            time_from_now_string = "{} month{}".format(month, months_plural)

            if month > 12:
                time_from_now_string = years_string

            net_income_calculations.append(
                {
                    "raise_applies_to_date": raise_applies_to_date,
                    "time_from_now": time_from_now_string,
                    "date_string": date_string,
                    "net_income": net_income,
                    "new_total": new_total,
                    "new_age": new_age,
                    "investment": investment,
                }
            )

        return net_income_calculations


TRANSACTION_TYPES = [
    ("ex", "Expense"),
    ("in", "Income"),
]


class MutedFieldMixin(models.Model):
    class Meta:
        abstract = True

    muted = models.BooleanField(
        default=False,
        help_text='This checkbox allows you to temporarily "mute" a transaction '
        "from appearing in any calculations.  Useful to get a quick "
        "idea of what your net income would look like without a "
        "particular transaction.",
    )
    __original_muted = None

    def __init__(self, *args, **kwargs):
        super(MutedFieldMixin, self).__init__(*args, **kwargs)
        self.__original_muted = self.muted

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.muted != self.__original_muted:
            # If muting/unmuting group, mute/unmute all group's transactions
            if isinstance(self, TransactionGroup):
                all_transactions = MonthlyTransaction.objects.filter(group=self).all()
                all_transactions.update(muted=self.muted)
            # If muting/unmuting transaction, check if we need to mute/unmute group
            elif isinstance(self, MonthlyTransaction):
                group_transactions = MonthlyTransaction.objects.filter(
                    group=self.group
                ).exclude(id=self.id)
                group_qs = TransactionGroup.objects.filter(id=self.group.id)
                if self.muted:
                    unmuted_transaction_in_group = group_transactions.filter(
                        muted=False
                    ).exists()
                    if not unmuted_transaction_in_group:
                        group_qs.update(muted=True)

                else:
                    muted_transaction_in_group = group_transactions.filter(
                        muted=True
                    ).exists()
                    if not muted_transaction_in_group:
                        group_qs.update(muted=False)

        super(MutedFieldMixin, self).save(force_insert, force_update, *args, **kwargs)
        self.__original_muted = self.muted


class TransactionGroup(MutedFieldMixin):
    group_type = models.CharField(max_length=2, choices=TRANSACTION_TYPES, default="ex")
    group_name = models.CharField(null=False, blank=False, max_length=100)

    def __str__(self):
        return "{}".format(self.group_name)

    def total(self):
        all_transactions = MonthlyTransaction.objects.filter(
            group=self, muted=False
        ).annotate(total=Sum(F("multiplier") * F("amount")))

        total = 0
        for transaction in all_transactions:
            total += transaction.total

        return total


class MonthlyTransaction(MutedFieldMixin):
    type = models.CharField(max_length=2, choices=TRANSACTION_TYPES, default="ex")
    user = models.ForeignKey(
        CustomUser, default=1, on_delete=models.SET_NULL, blank=True, null=True
    )
    name = models.CharField(null=False, blank=False, max_length=100)
    group = models.ForeignKey(TransactionGroup, on_delete=models.SET(1), default=1)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    multiplier = models.IntegerField(
        default=1,
        help_text="Amount will be multiplied by this value for a final "
        "total when this field is used in calculations.  "
        "This can be useful to track recurring expenses throughout "
        "the month, like groceries every week etc.",
    )

    def __str__(self):
        return "{}".format(self.name)
