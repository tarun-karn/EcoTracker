from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ActivitySubmissionForm
from .models import ActivitySubmission

class SubmitActivityView(LoginRequiredMixin, CreateView):
    model = ActivitySubmission
    form_class = ActivitySubmissionForm
    template_name = 'activities/submit_activity.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
