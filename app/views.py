from .forms import MonthlyTransactionForm, TransactionGroupForm
from .util import get_user, setup_db_first_time, get_model
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.contrib.auth import login
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import TransactionGroup
from django.views import View
import json


class HomeView(View):
    @staticmethod
    def get(request):
        min_years = 1
        max_years = 99
        years = int(request.GET.get("years", 1))
        years = int(years if min_years <= years <= max_years else min_years)
        ctx = {"years_to_project": years}

        user = get_user()
        if user:
            request.session["new_user"] = False

            login(request, user)

            ctx.update(
                {
                    "user": user,
                    "income_calculations": user.get_income_calculations(
                        years_to_project=years
                    ),
                    "net_income_calculations": user.get_net_income_calculations(
                        years_to_project=years
                    ),
                }
            )
        else:
            request.session["new_user"] = True
            user = setup_db_first_time()
            login(request, user)

            # Redirect to admin page for the user
            return redirect(user.get_admin_url())

        return TemplateResponse(request, "base.html", ctx)


class EditFormView(View):
    form = MonthlyTransactionForm()
    add_group_form = None
    template = "components/includes/edit_transaction_form.html"

    def get(self, request, object_id=None, object_type=None):
        ctx = {}
        model = get_model(object_type)

        if object_id:
            obj = model.objects.get(id=object_id)

            if isinstance(obj, TransactionGroup):
                self.form = TransactionGroupForm(instance=obj)
            else:
                self.form = MonthlyTransactionForm(instance=obj)
                self.add_group_form = TransactionGroupForm(instance=obj.group)

            ctx["add_group_form"] = self.add_group_form
            ctx["object"] = obj
        else:
            ctx["add_group_form"] = TransactionGroupForm()

        ctx["edit_form"] = self.form
        html = render_to_string(self.template, context=ctx, request=request)
        return JsonResponse({"success": True, "html": html}, status=200)

    def post(self, request, object_id=None, object_type=None):
        # Get model and initial forms using data from the POST
        model = get_model(object_type)
        self.add_group_form = TransactionGroupForm(request.POST)
        self.form = MonthlyTransactionForm(request.POST)
        if model == TransactionGroup:
            self.form = TransactionGroupForm(request.POST)

        # Get reference to object if ID was provided
        if object_id:
            obj = model.objects.get(id=object_id)
            if isinstance(obj, TransactionGroup):
                self.form = TransactionGroupForm(request.POST, instance=obj)
            else:
                self.form = MonthlyTransactionForm(request.POST, instance=obj)
                self.add_group_form = TransactionGroupForm(
                    request.POST, instance=obj.group
                )

        # Determine if user added a new group
        new_group = None
        if self.add_group_form.is_valid():
            new_group_name = self.add_group_form.cleaned_data["group_name"]
            new_group_exists = TransactionGroup.objects.filter(
                group_name=new_group_name
            ).exists()
            if new_group_name and not new_group_exists:
                new_group = self.add_group_form.save()
                # TODO flash message

        # Save the form/group
        if self.form.is_valid():
            self.form.instance.user = get_user()
            if new_group:
                self.form.instance.group = new_group
                self.form.instance.type = new_group.group_type

            self.form.save()
            # TODO flash message

        return redirect("home")


@method_decorator(csrf_exempt, name="dispatch")
class EditFormActionView(View):
    @staticmethod
    def get():
        return JsonResponse({}, status=405)

    @staticmethod
    def post(request):
        try:
            body = json.loads(request.body)
            object_id = body["objectId"]
            object_type = body["objectType"]
            action = body["action"]

            model = get_model(object_type)
            obj = model.objects.get(id=object_id)

            if action == "delete":
                # TODO flash message
                obj.delete()

        except KeyError as e:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Incomplete payload, missing: {}".format(e),
                }
            )

        return JsonResponse({"success": True}, status=200)
