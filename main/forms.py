from django import forms


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class UploadFileForm(forms.Form):
    job_description = forms.CharField(
        label="Job Description",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Paste the job requirements here...'
        })
    )

    files = forms.FileField(
        label="Upload CVs (PDF)",
        required=False ,
        widget=MultipleFileInput(attrs={
            'multiple': True,
            'class': 'form-control',
            'accept': '.pdf'
        })
    )