from django import forms
from django.utils.translation import gettext_lazy as _
from auctions.models import Comment, Listing


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "price", "category", "image"]
        labels = {"price": _("Starting Price"), "image": _("Image URL")}
        help_texts = {
            "title": _("Keep it short"),
            "category": _("Optional"),
            "image": _("Optional"),
        }
        widgets = {
            "description": forms.Textarea(
                attrs={"placeholder": _("Limit of 250 characters."), "rows": 5}
            ),
            # "image": forms.FileInput,
            "price": forms.NumberInput(
                attrs={"max": f"{1000000.00:.2f}", "min": 0.01, "step": "any"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].empty_label = "No Category"


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["post"]
        labels = {"post": ""}
        widgets = {
            "post": forms.Textarea(
                attrs={
                    "placeholder": _("Type your comment here. Max of 250 characters."),
                    "rows": 5,
                }
            )
        }


class EditForm(ListingForm):
    class Meta(ListingForm.Meta):
        exclude = ["price"]


class BidForm(forms.Form):
    value = forms.DecimalField(max_digits=9, decimal_places=2)
