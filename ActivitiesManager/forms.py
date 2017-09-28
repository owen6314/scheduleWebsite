from django import forms
from .models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ('title', 'description', 'begin_time', 'end_time', 'is_public', 'type', 'tags',)


class UploadFileForm(forms.Form):
    # title = forms.CharField(max_length=50, required=False)
    file = forms.FileField()