from .models import MonthlyTransaction, TransactionGroup
from django.forms import ModelForm, CharField


class MonthlyTransactionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MonthlyTransactionForm, self).__init__(*args, **kwargs)
        self.fields["group"].queryset = TransactionGroup.objects.filter(
            group_type=self.instance.type
        ).all()
        if self.instance.pk is not None:
            del self.fields["type"]

        self.fields["muted"].widget.attrs["class"] = "flex-horizontal"

    class Meta:
        model = MonthlyTransaction
        fields = "__all__"
        exclude = ["user"]


class TransactionGroupForm(ModelForm):
    group_name = CharField(required=False)

    class Meta:
        model = TransactionGroup
        fields = "__all__"
        exclude = ["user"]

    def __init__(self, *args, **kwargs):
        super(TransactionGroupForm, self).__init__(*args, **kwargs)
        if self.instance.pk is not None:
            self.fields["group_type"].widget.attrs["class"] = "readonly"

        self.fields["muted"].widget.attrs["class"] = "flex-horizontal"


class MonthlyTransactionsInlineForm(ModelForm):
    class Meta:
        model = MonthlyTransaction
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(MonthlyTransactionsInlineForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["group"].queryset = TransactionGroup.objects.filter(
                group_type=self.instance.type
            )


class MonthlyIncomeInlineForm(MonthlyTransactionsInlineForm):
    def __init__(self, *args, **kwargs):
        kwargs.update(initial={"type": "in"})
        super(MonthlyIncomeInlineForm, self).__init__(*args, **kwargs)
        self.fields["group"].queryset = TransactionGroup.objects.filter(group_type="in")
        self.fields["type"].widget.attrs["class"] = "readonly"


class MonthlyExpensesInlineForm(MonthlyTransactionsInlineForm):
    def __init__(self, *args, **kwargs):
        kwargs.update(initial={"type": "ex"})
        super(MonthlyExpensesInlineForm, self).__init__(*args, **kwargs)
        self.fields["group"].queryset = TransactionGroup.objects.filter(group_type="ex")
        self.fields["type"].widget.attrs["class"] = "readonly"
