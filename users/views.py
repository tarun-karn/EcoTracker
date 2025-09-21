from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .models import UserProfile, UserBadge
from .forms import CustomUserCreationForm
from activities.models import CarbonLog, ActivitySubmission
from ai_features.ai_services import EcoMentorAI
import io

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class UserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Update profile stats from CarbonLog
        profile.update_stats()
        
        # Get user badges
        user_badges = UserBadge.objects.filter(user=user).order_by('-earned_at')
        
        # Certificate eligibility
        certificate_milestone = 500
        is_eligible_for_certificate = profile.total_points >= certificate_milestone
        
        # Calculate values for template
        points_to_certificate = max(0, certificate_milestone - profile.total_points)
        progress_percentage = min(100, (profile.total_points / certificate_milestone) * 100) if certificate_milestone > 0 else 0

        context = {
            'user': user,
            'profile': profile,
            'user_badges': user_badges,
            'is_eligible_for_certificate': is_eligible_for_certificate,
            'certificate_milestone': certificate_milestone,
            'points_to_certificate': points_to_certificate,
            'progress_percentage': progress_percentage,
            'total_points': profile.total_points,  # Add this for backward compatibility
        }
        return render(request, 'users/profile.html', context)

@login_required
def generate_certificate_pdf(request):
    """Generate AI-enhanced PDF certificate with personalized content"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get user's eco-statistics
    total_points = user.carbonlog_set.aggregate(Sum('points_earned'))['points_earned__sum'] or 0
    total_carbon = user.carbonlog_set.aggregate(Sum('carbon_saved_kg'))['carbon_saved_kg__sum'] or 0
    activity_count = ActivitySubmission.objects.filter(user=user, status='APPROVED').count()
    
    if total_points < 500:
        return HttpResponse(b"Not eligible for a certificate.", status=403)
    
    # Generate AI-enhanced content
    ai_content = generate_ai_certificate_content(user, total_points, total_carbon, activity_count)
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="EcoChampion_Certificate_{user.username}.pdf"'
    
    # Create PDF buffer
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=30,
        alignment=1,  # Center
        textColor=Color(0.1, 0.6, 0.1)
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=20,
        alignment=1,
        textColor=Color(0.2, 0.2, 0.2)
    )
    
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Heading1'],
        fontSize=32,
        spaceAfter=30,
        alignment=1,
        textColor=Color(0.1, 0.7, 0.1)
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=15,
        alignment=1,
        leading=20
    )
    
    # Build certificate content
    story.append(Spacer(1, 50))
    story.append(Paragraph("🏆 CERTIFICATE OF ECO-ACHIEVEMENT 🌍", title_style))
    story.append(Paragraph("This certificate is proudly presented to", subtitle_style))
    
    # User name
    display_name = user.get_full_name() or user.username
    story.append(Paragraph(f"<b>{display_name}</b>", name_style))
    
    # AI-generated personalized content
    story.append(Paragraph(ai_content['achievement_text'], body_style))
    story.append(Paragraph(ai_content['impact_analysis'], body_style))
    story.append(Paragraph(ai_content['encouragement_message'], body_style))
    
    # Statistics section
    stats_text = f"""<br/><br/>
    <b>Your Environmental Impact Summary:</b><br/>
    🏆 Total Points Earned: {total_points:,}<br/>
    🌍 Carbon Footprint Reduced: {total_carbon:.2f} kg CO₂<br/>
    📊 Activities Completed: {activity_count}<br/>
    📅 Certificate Date: {timezone.now().strftime('%B %d, %Y')}<br/>
    """
    story.append(Paragraph(stats_text, body_style))
    
    story.append(Spacer(1, 50))
    story.append(Paragraph("<i>Continue your journey towards a sustainable future!</i>", subtitle_style))
    story.append(Paragraph("EcoTracker Platform Team", body_style))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF data and return response
    pdf_data = buffer.getvalue()
    buffer.close()
    response.write(pdf_data)
    
    return response


def generate_ai_certificate_content(user, total_points, total_carbon, activity_count):
    """Generate AI-enhanced certificate content"""
    
    # Calculate impact equivalents
    trees_equivalent = total_carbon / 22  # 22kg CO2 per tree per year
    cars_off_road = total_carbon / 4600  # Average car emits 4.6 tons CO2/year
    
    # Generate personalized achievement text
    if total_points >= 2000:
        achievement_level = "Eco-Champion"
        achievement_text = f"For exceptional environmental leadership and achieving the prestigious rank of <b>{achievement_level}</b>. Your dedication to sustainability has set an inspiring example for the entire campus community."
    elif total_points >= 1000:
        achievement_level = "Environmental Steward"
        achievement_text = f"For outstanding commitment to environmental protection and achieving the rank of <b>{achievement_level}</b>. Your consistent eco-friendly actions are making a real difference."
    else:
        achievement_level = "Eco-Warrior"
        achievement_text = f"For your valuable contribution to campus sustainability and achieving the rank of <b>{achievement_level}</b>. Every action you take brings us closer to a greener future."
    
    # Generate impact analysis
    impact_analysis = f"""Your environmental impact is equivalent to:
    🌳 Planting <b>{trees_equivalent:.1f} trees</b> and nurturing them for a full year
    🚗 Taking <b>{cars_off_road:.2f} cars</b> off the road for an entire year
    🏠 Powering an average home for <b>{total_carbon/365:.1f} days</b> with clean energy"""
    
    # Generate encouragement based on user's activity pattern
    try:
        eco_mentor = EcoMentorAI(user)
        # Get most recent activities to personalize message
        recent_activities = ActivitySubmission.objects.filter(
            user=user, status='APPROVED'
        ).order_by('-submitted_at')[:5]
        
        if recent_activities:
            activity_types = [sub.activity_type for sub in recent_activities]
            most_common = max(set(activity_types), key=activity_types.count)
            
            activity_messages = {
                'TREE': "Your tree planting efforts are creating lasting green legacies!",
                'RECYCLE': "Your recycling initiatives are closing the loop on waste!", 
                'CLEANUP': "Your cleanup drives are beautifying our shared spaces!",
                'AWARENESS': "Your awareness campaigns are inspiring others to act!",
                'ENERGY_SAVING': "Your energy conservation is reducing our carbon footprint!"
            }
            
            encouragement = activity_messages.get(most_common, "Your diverse eco-activities are making a comprehensive impact!")
        else:
            encouragement = "Your commitment to sustainability is building a better tomorrow!"
            
    except Exception:
        encouragement = "Your environmental consciousness is a beacon of hope for future generations!"
    
    encouragement_message = f"<b>Personal Message:</b> {encouragement} Keep leading by example and inspiring others to join the sustainability movement."
    
    return {
        'achievement_text': achievement_text,
        'impact_analysis': impact_analysis,
        'encouragement_message': encouragement_message,
        'achievement_level': achievement_level
    }
