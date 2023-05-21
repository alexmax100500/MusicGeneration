from django import forms


class UploadFileForm(forms.Form):
    template_name="form_template.html"
    title = forms.CharField(max_length=50)
    file = forms.FileField()