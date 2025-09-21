import io
import qrcode
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.csrf import csrf_exempt
from .models import Event, EventParticipant
from activities.models import CarbonLog
from django.utils.decorators import method_decorator

# Helper for staff check
def is_staff(user):
    return user.is_staff

class EventListView(LoginRequiredMixin, View):
    def get(self, request):
        events = Event.objects.all().order_by('-date')
        return render(request, 'events/event_list.html', {'events': events})

class EventDetailView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        return render(request, 'events/event_detail.html', {'event': event})

def generate_qr_code(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    # The data to encode in the QR code is the check-in URL
    checkin_url = request.build_absolute_uri(reverse('api-event-checkin', args=[event.id]))

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(checkin_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    # Serve the image
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)

    return HttpResponse(buffer, content_type='image/png')


@method_decorator(csrf_exempt, name='dispatch')
class EventCheckinAPI(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, event_id):
        user_id_to_checkin = request.POST.get('user_id')
        if not user_id_to_checkin:
            return JsonResponse({'status': 'error', 'message': 'User ID missing'}, status=400)

        event = get_object_or_404(Event, pk=event_id)
        user_to_checkin = get_object_or_404(request.user._meta.model, pk=user_id_to_checkin)

        # Check if user is already checked in
        if EventParticipant.objects.filter(event=event, user=user_to_checkin).exists():
            return JsonResponse({'status': 'error', 'message': f'{user_to_checkin.username} already checked in.'}, status=409)

        # Create the participant record
        EventParticipant.objects.create(event=event, user=user_to_checkin)

        # Award points and create a carbon log
        CarbonLog.objects.create(
            user=user_to_checkin,
            carbon_saved_kg=0, # Attendance doesn't directly save carbon unless specified
            points_earned=event.points_for_attendance
        )

        return JsonResponse({'status': 'success', 'message': f'Successfully checked in {user_to_checkin.username}!'})


@user_passes_test(is_staff)
def qr_scanner_view(request):
    return render(request, 'events/qr_scanner.html')
