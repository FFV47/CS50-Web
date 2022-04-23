import re
import markdown2 as md2
from django.shortcuts import redirect, render
from django import forms
from random import choice

from encyclopedia import util

# Global variable for error messages
message = ""


# FORMS
class NewEntry(forms.Form):
    title = forms.CharField(
        label="Title", label_suffix="", help_text="Please, keep it short", max_length=20
    )
    content = forms.CharField(
        label="Wiki Content",
        label_suffix="",
        help_text="Your text must be formatted in Markdown",
        widget=forms.Textarea,
    )
    edit_mode = forms.BooleanField(
        initial=False, widget=forms.HiddenInput, required=False
    )


# VIEWS
def index(request):
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


def search_entry(request):
    query = re.compile(request.GET["q"], re.IGNORECASE)
    results = []
    for entry in util.list_entries():
        match = query.search(entry)
        exact_match = query.fullmatch(entry)
        if exact_match:
            return redirect("encyclopedia:entry_page", entry)
        elif match:
            results.append(entry)
    if not results:
        global message
        message = f"Your search - '{request.GET['q']}' - did not match any documents"
        return redirect("encyclopedia:error")

    context = {"results": results}
    return render(request, "encyclopedia/search.html", context)


def entry_page(request, entry):
    if entry not in util.list_entries():
        global message
        message = "Page Not Found 404"
        return redirect("encyclopedia:error")
    entry_html = md2.markdown(util.get_entry(entry))
    context = {"entry_title": entry, "entry_content": entry_html}
    return render(request, "encyclopedia/entry_page.html", context)


def new_entry(request):
    if request.method == "POST":
        # binding data to the form
        form = NewEntry(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            edit_mode = form.cleaned_data["edit_mode"]
            entries = map(str.lower, util.list_entries())
            if title.lower() in entries and not edit_mode:
                global message
                message = "A page with this title already exists"
                return redirect("encyclopedia:error")
            util.save_entry(title, content)
            return redirect("encyclopedia:entry_page", title)
        # If form is not valid, we go back to the template with the form.
        # This time the form is no longer empty (unbound) so the HTML form will be
        # populated with the data previously submitted, where it can be edited and
        # corrected as required.
    else:
        form = NewEntry()
    return render(
        request,
        "encyclopedia/new_entry.html",
        {
            "form": form,
            "header_text": "Submit a new entry for the Wiki",
            "btn_text": "Submit Wiki Page",
        },
    )


def edit_entry(request, entry):
    content = util.get_entry(entry)
    form = NewEntry({"title": entry, "content": content, "edit_mode": True})
    return render(
        request,
        "encyclopedia/new_entry.html",
        {
            "form": form,
            "header_text": f"Edit {entry} page of the Wiki",
            "btn_text": "Save Changes",
        },
    )


def rand_entry(request):
    entries = util.list_entries()
    return redirect("encyclopedia:entry_page", choice(entries))


def error(request):
    return render(request, "encyclopedia/error.html", {"message": message})
