from django import forms
from .models import ActivitySubmission

class ActivitySubmissionForm(forms.ModelForm):
    class Meta:
        model = ActivitySubmission
        fields = ['activity_type', 'quantity', 'description', 'evidence']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
