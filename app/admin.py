from .forms import (
    MonthlyTransactionsInlineForm,
    MonthlyIncomeInlineForm,
    MonthlyExpensesInlineForm,
)
from .models import CustomUser, MonthlyTransaction, TransactionGroup
from django.shortcuts import redirect
from django.contrib import admin
from .apps import AppConfig
from .util import get_user


class MonthlyTransactionInline(admin.TabularInline):
    fields = ["type", "group", "name", "amount", "multiplier", "muted"]
    model = MonthlyTransaction
    extra = 0
    verbose_name = "Monthly Transaction"
    verbose_name_plural = "Monthly Transactions"
    form = MonthlyTransactionsInlineForm


class MonthlyIncomeTransactionsInline(MonthlyTransactionInline):
    verbose_name = "Monthly Income Transaction"
    verbose_name_plural = "Monthly Income Transactions"
    form = MonthlyIncomeInlineForm

    def get_queryset(self, request):
        return MonthlyTransaction.objects.filter(user=request.user, type="in").all()


class MonthlyExpenseTransactionsInline(MonthlyTransactionInline):
    verbose_name = "Monthly Expense Transaction"
    verbose_name_plural = "Monthly Expense Transactions"
    form = MonthlyExpensesInlineForm

    def get_queryset(self, request):
        return MonthlyTransaction.objects.filter(user=request.user, type="ex").all()


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    fields = [
        "name",
        "birth_date",
        "starting_value",
        "accent_color",
        "dark_mode",
        "toggle_raise",
        "raise_pct",
    ]
    save_on_top = True
    inlines = [MonthlyIncomeTransactionsInline, MonthlyExpenseTransactionsInline]
    change_form_template = "admin/custom_change_form.html"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        return redirect(get_user().get_admin_url())

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_save_and_continue"] = False
        return super(CustomUserAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context
        )


@admin.register(MonthlyTransaction)
class MonthlyTransactionAdmin(admin.ModelAdmin):
    list_display = ["type", "name", "group", "amount", "multiplier"]
    list_display_links = list_display
    list_filter = ["type", "group"]
    sortable_by = list_display
    search_fields = ["name", "group__group_name"]
    save_on_top = True
    fields = ["type", "name", "group", "amount", "multiplier", "muted"]


@admin.register(TransactionGroup)
class TransactionGroupAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display = ("group_name", "group_type", "muted")
    list_display_links = list_display
    list_filter = ["group_type", "group_name", "muted"]
    sortable_by = list_display
    search_fields = ["group_name"]
    save_on_top = True
    inlines = [MonthlyTransactionInline]


admin.site.site_header = "Finance by Month"
