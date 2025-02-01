from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import re
import os
from datetime import datetime, timedelta, timezone
import logging
from uuid import uuid4
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dating_site.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'datehubvk@gmail.com'
app.config['MAIL_PASSWORD'] = 'kghp rmfj xatn cdpd'  # Replace with your App Password
app.config['MAIL_DEFAULT_SENDER'] = 'datehubvk@gmail.com'

db = SQLAlchemy(app)
mail = Mail(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

# Set up logging
logging.basicConfig(level=logging.DEBUG)

login_manager = LoginManager(app)
login_manager.login_view = 'signin'

class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String(50), nullable=False)
    hobbies = db.Column(db.String(255))
    bio = db.Column(db.Text)
    image = db.Column(db.String(255))
    previous_relationships = db.Column(db.Integer, default=0)
    previous_dates = db.Column(db.Integer, default=0)
    insta_id = db.Column(db.String(100))
    ideal_weekend = db.Column(db.String(50))
    music_taste = db.Column(db.String(100))
    societies = db.Column(db.String(500))
    favorite_sports = db.Column(db.String(200))
    cgpa = db.Column(db.Float, nullable=True)
    leisure_activities = db.Column(db.String(100))
    personality_type = db.Column(db.String(50))
    sleep_schedule = db.Column(db.String(50))
    aspirations = db.Column(db.String(50))
    dream_date = db.Column(db.String(255))
    communication_style = db.Column(db.String(50))
    relationship_looking_for = db.Column(db.String(50))

class DateRequest(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    sender_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    place = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending')
    parent_request_id = db.Column(db.String(36), db.ForeignKey('date_request.id'))
    is_blind_date = db.Column(db.Boolean, default=False)
    last_altered_by = db.Column(db.String(36), db.ForeignKey('user.id'))
    last_action_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_requests')
    parent_request = db.relationship('DateRequest', remote_side=[id], backref='child_requests')

class Confession(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100))
    gender = db.Column(db.String(20))
    is_anonymous = db.Column(db.Boolean, default=False)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ConfessionLike(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    confession_id = db.Column(db.String(36), db.ForeignKey('confession.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'confession_id', name='unique_user_confession_like'),)

class OTP(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    email = db.Column(db.String(120), nullable=False)
    otp = db.Column(db.String(4), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime)

    def __init__(self, email, otp):
        self.email = email
        self.otp = otp
        self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def home():
    top_confessions = Confession.query.order_by(Confession.likes.desc()).limit(3).all()
    if current_user.is_authenticated:
        return render_template('dashboard.html', top_confessions=top_confessions)
    return render_template('index.html', top_confessions=top_confessions)

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(4)])

def send_otp_email(email, otp):
    try:
        msg = Message("Your OTP for DateHub.vk", recipients=[email])
        msg.body = f"Your OTP is: {otp}. It will expire in 10 minutes."
        mail.send(msg)
    except Exception as e:
        app.logger.error(f"Error sending email: {str(e)}")
        raise

@app.route('/verify_email', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def verify_email():
    if request.method == 'POST':
        email = request.form['email']

        if not re.match(r'[\w\.-]+@iitbbs\.ac\.in$', email):
            return jsonify({'error': 'Invalid email domain. Use iitbbs.ac.in email.'}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400

        try:
            otp = generate_otp()
            new_otp = OTP(email=email, otp=otp)
            db.session.add(new_otp)
            db.session.commit()

            send_otp_email(email, otp)

            return jsonify({'message': 'OTP sent to your email. Please verify to continue signup.'}), 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error in verify_email: {str(e)}")
            return jsonify({'error': 'An error occurred while sending OTP. Please try again later.'}), 500

    return render_template('verify_email.html')

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    email = request.form.get('email')
    otp = request.form.get('otp')
    
    if not email or not otp:
        return jsonify({'error': 'Email and OTP are required'}), 400

    otp_record = OTP.query.filter_by(email=email, otp=otp).first()

    current_time = datetime.now(timezone.utc)
    
    if otp_record:
        expires_at = otp_record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if current_time <= expires_at:
            db.session.delete(otp_record)
            db.session.commit()
            return jsonify({'message': 'OTP verified successfully', 'redirect': url_for('signup', email=email)}), 200
        else:
            return jsonify({'error': 'OTP has expired'}), 400
    else:
        return jsonify({'error': 'Invalid OTP'}), 400

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        app.logger.debug("Received POST request for signup")
        app.logger.debug(f"Form data: {request.form}")
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        gender = request.form['gender']
        branch = request.form['branch']
        year = request.form['year']
        state = request.form['state']
        hobbies = request.form['hobbies']
        bio = request.form['bio']
        previous_relationships = request.form['previous_relationships']
        previous_dates = request.form['previous_dates']
        insta_id = request.form['insta_id']
        ideal_weekend = request.form['ideal_weekend']
        music_taste = request.form['music_taste']
        societies = request.form.getlist('societies')
        favorite_sports = request.form.getlist('favorite_sports')
        cgpa = request.form.get('cgpa')
        if cgpa:
            cgpa = float(cgpa)
        else:
            cgpa = None
        leisure_activities = request.form['leisure_activities']
        personality_type = request.form.get('personality_type')
        sleep_schedule = request.form['sleep_schedule']
        aspirations = request.form['aspirations']
        dream_date = request.form['dream_date']
        communication_style = request.form.get('communication_style')
        relationship_looking_for = request.form['relationship_looking_for']

        hashed_password = generate_password_hash(password)
        new_user = User(
            email=email, password=hashed_password, name=name, gender=gender,
            branch=branch, year=year, state=state, hobbies=hobbies, bio=bio,
            previous_relationships=previous_relationships,
            previous_dates=previous_dates, insta_id=insta_id,
            ideal_weekend=ideal_weekend, music_taste=music_taste,
            societies=','.join(societies), favorite_sports=','.join(favorite_sports),
            cgpa=cgpa, leisure_activities=leisure_activities,
            personality_type=personality_type,
            sleep_schedule=sleep_schedule,
            aspirations=aspirations,
            dream_date=dream_date,
            communication_style=communication_style,
            relationship_looking_for=relationship_looking_for
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            app.logger.debug("User added successfully")
            return jsonify({'message': 'Signup successful', 'redirect': url_for('signin')}), 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error during signup: {str(e)}")
            return jsonify({'error': 'An error occurred during signup. Please try again.'}), 500

    email = request.args.get('email')
    if not email:
        return redirect(url_for('verify_email'))
    return render_template('signup.html', email=email)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return jsonify({'message': 'Signin successful', 'redirect': url_for('home')}), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 400

    return render_template('signin.html')

@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/users')
@limiter.limit("30 per minute")  # Adjust this value as needed
@login_required
def users():
    search_query = request.args.get('search', '')
    filters = {
        'year': request.args.get('year'),
        'sleep_schedule': request.args.get('sleep_schedule'),
        'personality_type': request.args.get('personality_type'),
        'ideal_weekend': request.args.get('ideal_weekend'),
        'favorite_sports': request.args.get('favorite_sports'),
        'societies': request.args.get('societies'),
        'leisure_activities': request.args.get('leisure_activities'),
        'music_taste': request.args.get('music_taste'),
        'gender': request.args.get('gender'),
        'state': request.args.get('state'),
        'relationship_looking_for': request.args.get('relationship_looking_for'),
    }
    
    query = User.query.filter(User.id != current_user.id)
    
    if search_query:
        query = query.filter(User.name.ilike(f'%{search_query}%'))
    
    for key, value in filters.items():
        if value:
            if key in ['societies', 'favorite_sports']:
                query = query.filter(getattr(User, key).like(f'%{value}%'))
            else:
                query = query.filter(getattr(User, key) == value)
    
    all_users = query.all()
    
    return render_template('users.html', users=all_users)

@app.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{current_user.id}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        current_user.image = unique_filename
        db.session.commit()
        
        return jsonify({'message': 'Image uploaded successfully', 'filename': unique_filename}), 200
    
    return jsonify({'error': 'File type not allowed'}), 400

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/profile/<user_id>')
@login_required
def get_profile(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'name': user.name,
            'gender': user.gender,
            'branch': user.branch,
            'year': user.year,
            'state': user.state,
            'hobbies': user.hobbies,
            'bio': user.bio,
            'image': user.image,
            'insta_id': user.insta_id,
            'ideal_weekend': user.ideal_weekend,
            'music_taste': user.music_taste,
            'favorite_sports': user.favorite_sports,
            'societies': user.societies,
            'leisure_activities': getattr(user, 'leisure_activities', 'Not specified'),
            'cgpa': user.cgpa,
            'personality_type': user.personality_type,
            'sleep_schedule': user.sleep_schedule,
            'aspirations': user.aspirations,
            'dream_date': user.dream_date,
            'communication_style': user.communication_style,
            'email': user.email,
            'relationship_looking_for': user.relationship_looking_for
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/blind_profile/<user_id>')
@login_required
def get_blind_profile(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'gender': user.gender,
            'year': user.year,
            'relationship_looking_for': user.relationship_looking_for,
            'state': user.state,
            'ideal_weekend': user.ideal_weekend,
            'music_taste': user.music_taste,
            'sleep_schedule': user.sleep_schedule,
            'leisure_activities': getattr(user, 'leisure_activities', 'Not specified'),
            'aspirations': user.aspirations,
            'personality_type': user.personality_type,
            'communication_style': user.communication_style
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/send_date_request', methods=['POST'])
@login_required
def send_date_request():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        receiver_id = data.get('receiver_id')
        date_str = data.get('date')
        time_str = data.get('time')
        place = data.get('place')
        is_blind_date = data.get('is_blind_date', False)

        if not all([receiver_id, date_str, time_str, place]):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Invalid date or time format'}), 400

        new_request = DateRequest(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            date=date,
            time=time,
            place=place,
            is_blind_date=is_blind_date
        )
        db.session.add(new_request)
        db.session.commit()

        return jsonify({'message': 'Date request sent successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error in send_date_request: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.route('/dates')
@login_required
def dates():
    user_id = current_user.id
    sent_requests = DateRequest.query.filter_by(sender_id=user_id).order_by(DateRequest.last_action_time.desc()).all()
    received_requests = DateRequest.query.filter_by(receiver_id=user_id).order_by(DateRequest.last_action_time.desc()).all()
    
    return render_template('dates.html', sent_requests=sent_requests, received_requests=received_requests, current_user=current_user)

@app.route('/date_requests')
@login_required
def date_requests():
    user_id = current_user.id
    received_requests = DateRequest.query.filter_by(receiver_id=user_id).all()
    sent_requests = DateRequest.query.filter_by(sender_id=user_id).all()
    
    return render_template('date_requests.html', received_requests=received_requests, sent_requests=sent_requests)

@app.route('/respond_to_date_request', methods=['POST'])
@login_required
def respond_to_date_request():
    data = request.json
    request_id = data.get('request_id')
    response = data.get('response')
    new_date = data.get('new_date')
    new_time = data.get('new_time')
    new_place = data.get('new_place')

    date_request = DateRequest.query.get(request_id)
    if not date_request or (date_request.receiver_id != current_user.id and date_request.sender_id != current_user.id):
        return jsonify({'error': 'Invalid request'}), 400

    if response == 'accept':
        date_request.status = 'accepted'
    elif response == 'deny' or response == 'cancel':
        date_request.status = 'denied'
    elif response == 'alter':
        date_request.date = datetime.strptime(new_date, '%Y-%m-%d').date()
        date_request.time = datetime.strptime(new_time, '%H:%M').time()
        date_request.place = new_place
        date_request.status = 'altered'
        date_request.last_altered_by = current_user.id
        # Swap the sender and receiver for the next round of changes
        date_request.sender_id, date_request.receiver_id = date_request.receiver_id, date_request.sender_id

    date_request.last_action_time = datetime.utcnow()

    try:
        db.session.commit()
        return jsonify({'message': 'Response submitted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in respond_to_date_request: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.route('/user_dates')
@login_required
def user_dates():
    user_id = current_user.id
    sent_requests = DateRequest.query.filter_by(sender_id=user_id).all()
    received_requests = DateRequest.query.filter_by(receiver_id=user_id).all()
    
    dates = []
    for request in sent_requests + received_requests:
        other_user = request.receiver if request.sender_id == user_id else request.sender
        dates.append({
            'id': request.id,
            'date': request.date.strftime('%Y-%m-%d'),
            'time': request.time.strftime('%H:%M'),
            'place': request.place,
            'status': request.status,
            'other_user': other_user.name,
            'is_sender': request.sender_id == user_id
        })
    
    return jsonify(dates)

@app.route('/blind_dates')
@login_required
def blind_dates():
    filters = {
        'gender': request.args.get('gender'),
        'year': request.args.get('year'),
        'relationship_looking_for': request.args.get('relationship_looking_for'),
        'state': request.args.get('state'),
        'ideal_weekend': request.args.get('ideal_weekend'),
        'music_taste': request.args.get('music_taste'),
        'sleep_schedule': request.args.get('sleep_schedule'),
        'leisure_activities': request.args.get('leisure_activities'),
        'aspirations': request.args.get('aspirations'),
        'personality_type': request.args.get('personality_type'),
        'communication_style': request.args.get('communication_style'),
    }
    
    query = User.query.filter(User.id != current_user.id)
    
    for key, value in filters.items():
        if value:
            query = query.filter(getattr(User, key) == value)
    
    all_users = query.all()
    
    # Shuffle the users randomly
    import random
    random.shuffle(all_users)
    
    return render_template('blind_dates.html', users=all_users)

@app.route('/confessions')
def confessions():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    confessions = Confession.query.order_by(Confession.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    liked_confessions = set()
    if current_user.is_authenticated:
        liked_confessions = set(ConfessionLike.query.filter_by(user_id=current_user.id).with_entities(ConfessionLike.confession_id).all())
    
    return render_template('confessions.html', confessions=confessions, liked_confessions=liked_confessions)

@app.route('/submit_confession', methods=['POST'])
@login_required
def submit_confession():
    content = request.form.get('content')
    is_anonymous = request.form.get('is_anonymous') == 'on'
    
    if not content:
        return jsonify({'error': 'Confession content is required'}), 400
    
    new_confession = Confession(
        content=content,
        author=current_user.name if not is_anonymous else None,
        gender=current_user.gender if not is_anonymous else None,
        is_anonymous=is_anonymous
    )
    
    db.session.add(new_confession)
    db.session.commit()
    
    return redirect(url_for('confessions'))

@app.route('/like_confession/<confession_id>', methods=['POST'])
@login_required
def like_confession(confession_id):
    confession = Confession.query.get_or_404(confession_id)
    like = ConfessionLike.query.filter_by(user_id=current_user.id, confession_id=confession.id).first()
    
    if like:
        db.session.delete(like)
        confession.likes -= 1
    else:
        new_like = ConfessionLike(user_id=current_user.id, confession_id=confession.id)
        db.session.add(new_like)
        confession.likes += 1
    
    db.session.commit()
    
    return jsonify({'likes': confession.likes, 'liked': like is None})

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    try:
        data = request.form
        user = User.query.get(current_user.id)
        
        # Update user fields
        user.name = data.get('name', user.name)
        user.bio = data.get('bio', user.bio)
        user.hobbies = data.get('hobbies', user.hobbies)
        user.insta_id = data.get('insta_id', user.insta_id)
        user.ideal_weekend = data.get('ideal_weekend', user.ideal_weekend)
        user.music_taste = data.get('music_taste', user.music_taste)
        user.dream_date = data.get('dream_date', user.dream_date)
        user.sleep_schedule = data.get('sleep_schedule', user.sleep_schedule)
        user.aspirations = data.get('aspirations', user.aspirations)
        user.personality_type = data.get('personality_type', user.personality_type)
        user.communication_style = data.get('communication_style', user.communication_style)
        user.state = data.get('state', user.state)
        user.cgpa = float(data.get('cgpa')) if data.get('cgpa') else user.cgpa
        user.relationship_looking_for = data.get('relationship_looking_for', user.relationship_looking_for)
        
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error updating profile: {str(e)}")
        return jsonify({'error': 'An error occurred while updating your profile'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Rate limit exceeded. Please try again later."), 429

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

