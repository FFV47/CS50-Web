from django import forms
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect, render


class NewTaskForm(forms.Form):
    task = forms.CharField(label="New Task")


# Create your views here.
def index(request):
    if "tasks" not in request.session:
        request.session["tasks"] = []
    return render(request, "tasks/index.html", {"tasks": request.session["tasks"]})


def add(request):
    if request.method == "POST":
        form = NewTaskForm(request.POST)
        if form.is_valid():
            task = form.cleaned_data["task"]
            request.session["tasks"] += [task]
            print(request.session["tasks"])
            return redirect("tasks:index")
        else:
            context = {"form": form}
            return render(request, "tasks/add.html", context)
    if "tasks" not in request.session:
        request.session["tasks"] = []
    context = {"form": NewTaskForm()}
    return render(request, "tasks/add.html", context)
