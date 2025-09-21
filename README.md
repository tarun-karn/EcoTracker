# 🌿 EcoTracker - Advanced Campus Sustainability Platform

[![Django](https://img.shields.io/badge/Django-5.0.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.0-blue.svg)](https://tailwindcss.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.0-orange.svg)](https://www.chartjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

EcoTracker is a comprehensive Django web application designed to promote campus sustainability through gamification, real-time tracking, and community engagement. The platform empowers students and faculty to track eco-friendly activities, compete in teams, earn badges, and generate meaningful environmental impact.

## 🌟 Key Features

### 🎮 **Gamification System**
- **Progressive Badges**: Bronze → Silver → Gold → Platinum → Eco Champion
- **Activity-Specific Badges**: Tree Lover, Recycling Hero, Cleanup Master, Energy Saver
- **Level Progression**: Visual progress tracking with percentage indicators
- **Points System**: Earn points for every validated eco-activity

### 📊 **Real-Time Analytics**
- **Interactive Dashboard**: Chart.js powered carbon savings visualization
- **Personal Metrics**: Track individual CO₂ savings and points
- **Campus-Wide Statistics**: Compare personal impact with community totals
- **30-Day Trends**: Historical data analysis and progress tracking

### 👥 **Team Competition**
- **Team Creation**: Form eco-teams with friends and classmates
- **Competitive Leaderboards**: Individual and team rankings
- **Collaborative Goals**: Work together for collective environmental impact
- **Team Statistics**: Aggregate team performance metrics

### 📱 **QR Code Event System**
- **Event Management**: Create and manage eco-events
- **QR Code Generation**: Automatic QR code creation for events
- **Mobile Scanner**: Html5-qrcode powered scanning interface
- **Instant Check-in**: Real-time event participation tracking

### 🤖 **AI Eco Assistant**
- **Smart Chatbot**: Rule-based eco-tips and recommendations
- **Personalized Advice**: Activity suggestions based on user history
- **Progress Insights**: Points tracking and goal recommendations
- **24/7 Availability**: Always available for eco-guidance

### 📜 **Achievement Certificates**
- **PDF Generation**: ReportLab powered certificate creation
- **Milestone Recognition**: Automated certificate generation at 500+ points
- **Professional Design**: Branded certificates with user achievements
- **Download & Share**: Instantly downloadable achievement certificates

### 🛡️ **Admin Management**
- **Enhanced Admin Interface**: Rich admin panels with visual indicators
- **Bulk Operations**: Approve/reject multiple submissions simultaneously
- **User Analytics**: Comprehensive user statistics and badge management
- **Evidence Review**: Streamlined activity approval workflow

## 🚀 **Live Demo**

🌐 **[Visit Live Demo](https://eco-track-sg2k.onrender.com/)**

### 🎯 **Demo Credentials**
```
👤 Demo Users (username/password):
• tarun/password123     - High performer (Gold level, 8 badges)
• aashish/password123   - Moderate performer (Silver level, 5 badges)
• yuvraj/password123    - Regular user (Bronze level, 3 badges)
• diana/password123     - Top performer (Eco Champion, 9 badges)
• eve/password123       - New user (2 badges)

🔧 Admin Access:
• admin2/[contact for password]
```

## 🛠️ **Local Setup & Installation**

### **Prerequisites**
- Python 3.8+ installed on your system
- Git installed (optional, for cloning)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### **Step 1: Get the Project**
```bash
# Option A: If you have the project folder already
cd "path/to/your/eco_tracker"

# Option B: Clone from repository (if applicable)
git clone <your-repo-url>
cd eco_tracker
```

### **Step 2: Create Virtual Environment**
```bash
# Windows
py -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 4: Database Setup**
```bash
# Run migrations
py manage.py migrate

# Create superuser (admin account)
py manage.py createsuperuser
# Follow prompts to create admin username/password

# Create achievements data
py manage.py create_achievements

# Load demo data (recommended for testing)
py manage.py seed_data --reset
```

### **Step 5: Run the Server**
```bash
py manage.py runserver
```

### **Step 6: Access the Application**
Open your browser and go to:
- **Main App**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

---

## 🎮 **Quick Start Guide**

### **Demo User Accounts**
After running `py manage.py seed_data --reset`, you can login with:

```
👤 Student Accounts:
• tarun/password123     - Gold level (high performer)
• aashish/password123   - Silver level (moderate)
• yuvraj/password123    - Bronze level (regular)
• diana/password123     - Eco Champion (top performer)
• eve/password123       - Newbie (new user)

🔧 Admin Account:
• Use the superuser account you created in Step 4
```

### **First Steps After Login**
1. **Dashboard**: View your points and carbon savings chart
2. **Submit Activity**: Click "Log New Activity" to submit an eco-activity
3. **View Profile**: See your badges and level progress
4. **Check Leaderboard**: See how you rank against other users
5. **Try Chatbot**: Click the chat icon (bottom right) for eco-tips
6. **Admin Approval**: Login to admin panel to approve pending activities

---

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

**Issue**: `ModuleNotFoundError: No module named 'django'`
```bash
# Solution: Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

**Issue**: `python/py command not found`
```bash
# Try different Python commands:
python manage.py runserver
python3 manage.py runserver
py manage.py runserver
```

**Issue**: Static files not loading
```bash
# Collect static files
py manage.py collectstatic
```

**Issue**: Database errors
```bash
# Reset database
rm db.sqlite3  # or delete db.sqlite3 file
py manage.py migrate
py manage.py seed_data --reset
```

### **Port Already in Use**
```bash
# Run on different port
py manage.py runserver 8080
# Then access: http://127.0.0.1:8080/
```

---
- **User Authentication**: Secure sign-up, login, and profile management.
- **Activity Logging**: Users can submit activities like tree planting, recycling, etc., with evidence.
- **Admin Approval Workflow**: Admins review and approve submissions, automatically awarding points and calculating carbon savings.
- **Team Competitions**: Users can join teams and compete on a team-based leaderboard.
- **Real-time Dashboard**: Visualizes personal and campus-wide carbon savings with Chart.js.
- **QR Code Event Check-in**: Admins can generate QR codes for events; organizers can scan them to check participants in.
- **PDF Certificates**: Automatically generate PDF certificates for users who reach certain milestones.
- **AI Eco-Chatbot**: A helpful chatbot to answer questions and provide eco-tips.

## 🛠️ Tech Stack
- **Backend**: Django 5.x, Python
- **Database**: SQLite (default), PostgreSQL (production-ready)
- **Frontend**: Django Templates, Tailwind CSS
- **Libraries**: `qrcode`, `Pillow`, `ReportLab`, `Chart.js`, `html5-qrcode`

## 🚀 Getting Started

**1. Clone the repository:**
```bash
git clone https://github.com/your-username/eco_tracker.git
cd eco_tracker
```

**2. Set up the environment:**
```bash
# Create and activate a virtual environment
py -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**3. Set up the database:**
```bash
py manage.py migrate
```

**4. Create a superuser:**
```bash
py manage.py createsuperuser
```

**5. (Optional) Seed the database with demo data:**
This will create sample users (e.g., username: `alice`, password: `password123`), teams, and activities.
```bash
py manage.py seed_data
```

**6. Run the development server:**
```bash
py manage.py runserver
```
The application will be available at `http://127.0.0.1:8000`.

## 🧪 Running Tests
To run the unit tests for the application:
```bash
py manage.py test
```

## 📱 Demo Walkthrough

### Elevator Pitch (30 seconds):
"Our planet faces a climate crisis, and student campuses are key to driving change. EcoTracker is a Django-powered web app that gamifies sustainability. Students submit eco-friendly activities like tree planting and recycling, earning points for themselves and their teams. We feature real-time carbon saving dashboards, competitive leaderboards, and even a helpful AI chatbot. With features like QR code check-in for green events, EcoTracker makes sustainability engaging, competitive, and rewarding for the entire campus community."

### Demo Steps (2 minutes):

1. **Homepage & Login** (0:00-0:20): "This is our landing page. I'll log in as a student, 'alice'." (Log in) "This takes me to my personal dashboard."

2. **Dashboard & Activity Submission** (0:20-0:45): "Here, I can see my total points and the carbon I've saved. Let's log a new activity." (Go to submit form, fill it out for 'Recycling' with a quantity of 5kg, submit). "My submission is now pending admin approval."

3. **Admin Approval & Leaderboard** (0:45-1:10): (Switch to another browser/admin panel). "As a campus admin, I see Alice's submission. The evidence looks good, so I'll approve it." (Approve it). (Switch back to Alice's view and refresh). "And just like that, my points and carbon stats have updated! This also affects our campus leaderboard, where my team, the Green Giants, is now climbing the ranks." (Show leaderboard page).

4. **Event QR Code Check-in** (1:10-1:40): "We also make green events interactive. Here's an event page with a unique QR code." (Show event detail). "An organizer can use our scanner page..." (Show scanner page, scan the QR code). "...enter my user ID, and I'm checked in, instantly earning points."

5. **Chatbot & Certificate** (1:40-2:00): "Finally, if I ever need help, our EcoBot can give me tips or check my points." (Ask the chatbot a question). "And because I've earned over 500 points, I've unlocked this downloadable PDF certificate to recognize my contribution!" (Show profile and click download).

## 🏗️ Project Structure
```
eco_tracker/
├── config/                 # Django project settings
├── core/                   # Core app (homepage)
├── users/                  # User authentication & profiles
├── activities/             # Activity submission & tracking
├── events/                 # Event management & QR codes
├── teams/                  # Team management
├── dashboard/              # Dashboard & leaderboards
├── templates/              # HTML templates
├── media/                  # User uploaded files
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

### Carbon Calculation Factors
The app uses configurable carbon savings factors in `config/settings.py`:
- Tree Plantation: 22.0 kg CO₂ per tree per year
- Recycling: 1.5 kg CO₂ per kg of recyclables
- Clean-up: 0.5 kg CO₂ per kg of waste collected
- Awareness: 5.0 kg CO₂ per hour of participation
- Energy Saving: 0.85 kg CO₂ per kWh saved

### Points System
- 10 points per unit of activity (e.g., 10 points per tree planted)
- 25 points for event attendance
- Certificate milestone: 500 points

## 🚀 Deployment

### Production Settings
Before deploying, update `config/settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
```

### Static Files
```bash
py manage.py collectstatic
```

### Database Migration
```bash
py manage.py migrate
```

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License
This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments
- Django community for the excellent framework
- Tailwind CSS for beautiful styling
- Chart.js for data visualization
- ReportLab for PDF generation
- html5-qrcode for QR scanning functionality
#   E c o T r a c k e r  
 #   E c o T r a c k e r  
 