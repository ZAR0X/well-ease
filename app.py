import re
import os
import json
import requests
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app=Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://zarox:newnew@localhost/flask_auth'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Explicit table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    time_of_day = db.Column(db.String(50), nullable=False)  # e.g., "Morning", "Afternoon", "Evening"
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.description}>'

# Streak Model
class Streak(db.Model):
    __tablename__ = 'streaks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Streak {self.user_id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Regex Validation Functions
def validate_username(username):
    """Validate username: alphanumeric, '.', '_' only."""
    return bool(re.match(r'^[a-zA-Z0-9._]+$', username))

def validate_email(email):
    """Validate email: strict Gmail regex."""
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email))

def validate_password(password):
    """Validate password: minimum 8 characters."""
    return len(password) >= 8


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
        description = request.form.get('description')
        time_of_day = request.form.get('time_of_day')

        if not description or not time_of_day:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('tasks'))

        task = Task(user_id=current_user.id, description=description, time_of_day=time_of_day)
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks'))

    user_tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('tasks.html', tasks=user_tasks, user=current_user)

@app.route('/complete_task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to complete this task.', 'danger')
        return redirect(url_for('tasks'))

    task.completed = True
    db.session.commit()

    # Check if the user has an active streak
    active_streak = Streak.query.filter_by(user_id=current_user.id, is_active=True).first()
    if active_streak:
        active_streak.end_date = datetime.utcnow()
        active_streak.is_active = False
        db.session.commit()

    # Start a new streak
    new_streak = Streak(user_id=current_user.id)
    db.session.add(new_streak)
    db.session.commit()

    flash('Task marked as completed!', 'success')
    return redirect(url_for('tasks'))

@app.route('/leaderboard')
def leaderboard():
    # Get top 25 users with the highest streaks
    top_users = db.session.query(
        User.username,
        db.func.max(Streak.end_date - Streak.start_date).label('longest_streak')
    ).join(Streak, User.id == Streak.user_id
    ).group_by(User.id
    ).order_by(db.desc('longest_streak')
    ).limit(25).all()

    # Get weekly streaks
    weekly_streaks = db.session.query(
        User.username,
        db.func.max(Streak.end_date - Streak.start_date).label('longest_streak')
    ).join(Streak, User.id == Streak.user_id
    ).filter(Streak.start_date >= datetime.utcnow() - timedelta(days=7)
    ).group_by(User.id
    ).order_by(db.desc('longest_streak')
    ).limit(25).all()

    return render_template('leaderboard.html', top_users=top_users, weekly_streaks=weekly_streaks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        if not validate_email(email):
            flash('Please enter a valid Gmail address.', 'danger')

        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:  # In a real app, use password hashing (e.g., bcrypt)
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validate username
        if not validate_username(username):
            flash('Username can only contain alphanumeric characters, ".", and "_".', 'danger')
            return redirect(url_for('signup'))

        # Validate email
        if not validate_email(email):
            flash('Please enter a valid Gmail address.', 'danger')
            return redirect(url_for('signup'))

        # Validate password
        if not validate_password(password):
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('signup'))

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))

        # Check if email already registered
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('signup'))

        # Create new user
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route('/bmi_final')
def bmi():
    return render_template('bmi_final.html')

@app.route('/Calorie-Counter')
def CalCount():
    return render_template('Calorie-Counter.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/video')
def vid():
    return render_template('video.html')


# Calorie Counter (meal)

@app.route('/submit', methods=['POST'])
def submit():
    output = request.form.to_dict()
    food_item = output['meal1']

    end_pt_url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    query = {
        "query": food_item,
    }

    headers = {
        "x-app-id": "66e88fcd",
        "x-app-key": "915bd34e3996d68e870d3be75c07b467",
        "Content-Type": "application/json"
    }

    r = requests.post(end_pt_url, headers=headers, json=query)
    data = json.loads(r.text)
    print(data)
    for food in data['foods']:
        name = food['food_name']
        cal = food['nf_calories']
        serving_qty = food["serving_qty"]
        serving_unit = food["serving_unit"]
        return render_template('result.html', cal=cal)

# bmi counter

@app.route('/bmi', methods=['POST'])
def bmi_res():
    output = request.form.to_dict()
    height = int(output['height'])
    weight = int(output['weight'])
    height_ = int(height) / 100
    bmi = (weight / (height ** 2)) * 10000
    if bmi <= 18.5:
        bmi_ = 'Underweight'
        bmi__ = 'Underweight'

    elif 18.5 < bmi <= 24.9:
        bmi_ = 'Normal'
        bmi__ = 'Normal'

    elif 25 <= bmi <= 29.9:
        bmi_ = 'Overweight'
        bmi__ = 'Overweight'

    elif 30 <= bmi <= 39.9:
        bmi_ = 'Obese'
        bmi__ = 'Obese'
    elif bmi >= 40:
        bmi_ = 'Morbidly'
        bmi__ = 'Morbidly Obese'
    else:
        bmi_ = 'Incorrect'
        bmi__ = 'Incorrect input'
    return render_template('bmi.html', bmi=round(bmi,2), bmi_ = bmi_, bmi__ = bmi__)
    
# Calorie counter (exercise)

@app.route('/result', methods=['POST'])
def calculate_calories_burnt():
    exercise = request.form.get('exercise')
    gender = request.form.get('gender')
    weight = float(request.form.get('weight'))
    height = float(request.form.get('height'))
    age = int(request.form.get('age'))

    # Make API request to calculate calories burnt
    end_pt_url = "https://trackapi.nutritionix.com/v2/natural/exercise"

    query = {
        "query": exercise,
        "gender": gender,
        "weight_kg": weight,
        "height_cm": height,
        "age": age
    }


    headers = {
        "x-app-id": "66e88fcd",
        "x-app-key": "915bd34e3996d68e870d3be75c07b467",
        "Content-Type": "application/json"
    }

    response = requests.post(end_pt_url, headers=headers, json=query)
    data = json.loads(response.text)

    exercise_details = []
    for exercise in data['exercises']:
        name = exercise['name']
        calories_burnt = exercise['nf_calories']
        duration = exercise["duration_min"]
        exercise_details.append((name, calories_burnt, duration))

    return render_template('submit.html', calories_burnt=calories_burnt)


app.static_folder = 'static'

if __name__=='__main__':
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)