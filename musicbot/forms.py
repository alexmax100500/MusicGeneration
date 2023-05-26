from django import forms


class UploadFileForm(forms.Form):
    template_name="form_template.html"
    file = forms.FileField()