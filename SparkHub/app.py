from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import re
import os
from datetime import datetime
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dating_site.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String(50), nullable=False)  # New field for state
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
    cgpa = db.Column(db.Float, nullable=True) # Updated CGPA field to allow null
    leisure_activities = db.Column(db.String(100))
    personality_type = db.Column(db.String(50))
    sleep_schedule = db.Column(db.String(50))
    aspirations = db.Column(db.String(50))
    dream_date = db.Column(db.String(255))
    communication_style = db.Column(db.String(50)) # Added communication_style field
    relationship_looking_for = db.Column(db.String(50)) # Added relationship_looking_for field

class DateRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    place = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, denied, altered
    parent_request_id = db.Column(db.Integer, db.ForeignKey('date_request.id'))
    is_blind_date = db.Column(db.Boolean, default=False)  # New field
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_requests')
    parent_request = db.relationship('DateRequest', remote_side=[id], backref='child_requests')

class Confession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100))
    gender = db.Column(db.String(20))  # Add this line
    is_anonymous = db.Column(db.Boolean, default=False)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ConfessionLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    confession_id = db.Column(db.Integer, db.ForeignKey('confession.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'confession_id', name='unique_user_confession_like'),)

@app.route('/')
def home():
    top_confessions = Confession.query.order_by(Confession.likes.desc()).limit(3).all()
    if 'user_id' in session:
        return render_template('dashboard.html', top_confessions=top_confessions)
    return render_template('index.html', top_confessions=top_confessions)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        name = request.form['name']
        gender = request.form['gender']
        branch = request.form['branch']
        year = request.form['year']
        state = request.form['state']  # New field
        hobbies = request.form['hobbies']
        bio = request.form['bio']
        previous_relationships = request.form['previous_relationships']
        previous_dates = request.form['previous_dates']
        insta_id = request.form['insta_id']
        ideal_weekend = request.form['ideal_weekend']
        music_taste = request.form['music_taste']
        societies = request.form['societies']
        favorite_sports = request.form['favorite_sports']
        cgpa = request.form.get('cgpa') # Updated CGPA handling
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
        relationship_looking_for = request.form['relationship_looking_for'] # Added line to get relationship_looking_for

        if not re.match(r'[\w\.-]+@iitbbs\.ac\.in$', email):
            return jsonify({'error': 'Invalid email domain. Use iitbbs.ac.in email.'}), 400

        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match.'}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(
            email=email, password=hashed_password, name=name, gender=gender,
            branch=branch, year=year, state=state, hobbies=hobbies, bio=bio,
            previous_relationships=previous_relationships,
            previous_dates=previous_dates, insta_id=insta_id,
            ideal_weekend=ideal_weekend, music_taste=music_taste,
            societies=societies, favorite_sports=favorite_sports,
            cgpa=cgpa, leisure_activities=leisure_activities,
            personality_type=personality_type,
            sleep_schedule=sleep_schedule,
            aspirations=aspirations,
            dream_date=dream_date,
            communication_style=communication_style,
            relationship_looking_for=relationship_looking_for
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'Signup successful'}), 200

    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name #Added to store username in session
            return jsonify({'message': 'Signin successful'}), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 400

    return render_template('signin.html')

@app.route('/signout')
def signout():
    session.pop('user_id', None)
    session.pop('user_name', None) #Added to remove username from session
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/users')
def users():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    
    search_query = request.args.get('search', '')
    filters = {
        'ideal_weekend': request.args.get('ideal_weekend'),
        'music_taste': request.args.get('music_taste'),
        'societies': request.args.get('societies'),
        'favorite_sports': request.args.get('favorite_sports'),
        'leisure_activities': request.args.get('leisure_activities'),
        'aspirations': request.args.get('aspirations'),
    }
    
    query = User.query.filter(User.id != session['user_id'])
    
    if search_query:
        query = query.filter(User.name.ilike(f'%{search_query}%'))
    
    for key, value in filters.items():
        if value:
            if key == 'societies':
                query = query.filter(User.societies.like(f'%{value}%'))
            else:
                query = query.filter(getattr(User, key) == value)
    
    all_users = query.all()
    return render_template('users.html', users=all_users)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{session['user_id']}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        user = User.query.get(session['user_id'])
        user.image = unique_filename
        db.session.commit()
        
        return jsonify({'message': 'Image uploaded successfully', 'filename': unique_filename}), 200
    
    return jsonify({'error': 'File type not allowed'}), 400

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/profile/<int:user_id>')
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

@app.route('/blind_profile/<int:user_id>')
def get_blind_profile(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'branch': user.branch,
            'year': user.year,
            'hobbies': user.hobbies,
            'bio': user.bio,
            'ideal_weekend': user.ideal_weekend,
            'music_taste': user.music_taste,
            'favorite_sports': user.favorite_sports,
            'societies': user.societies,
            'leisure_activities': getattr(user, 'leisure_activities', 'Not specified'),
            'sleep_schedule': user.sleep_schedule,
            'aspirations': user.aspirations,
            'dream_date': user.dream_date,
            'communication_style': user.communication_style,
            'state': user.state,
            'personality_type': user.personality_type,
            'relationship_looking_for': user.relationship_looking_for
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/send_date_request', methods=['POST'])
def send_date_request():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

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
            sender_id=session['user_id'],
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
def dates():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    
    user_id = session['user_id']
    sent_requests = DateRequest.query.filter_by(sender_id=user_id).all()
    received_requests = DateRequest.query.filter_by(receiver_id=user_id).all()
    
    return render_template('dates.html', sent_requests=sent_requests, received_requests=received_requests)

@app.route('/date_requests')
def date_requests():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    
    user_id = session['user_id']
    received_requests = DateRequest.query.filter_by(receiver_id=user_id).all()
    sent_requests = DateRequest.query.filter_by(sender_id=user_id).all()
    
    return render_template('date_requests.html', received_requests=received_requests, sent_requests=sent_requests)

@app.route('/respond_to_date_request', methods=['POST'])
def respond_to_date_request():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    data = request.json
    request_id = data.get('request_id')
    response = data.get('response')
    new_date = data.get('new_date')
    new_time = data.get('new_time')
    new_place = data.get('new_place')

    date_request = DateRequest.query.get(request_id)
    if not date_request or (date_request.receiver_id != session['user_id'] and date_request.sender_id != session['user_id']):
        return jsonify({'error': 'Invalid request'}), 400

    if response == 'accept':
        date_request.status = 'accepted'
    elif response == 'deny' or response == 'cancel':
        date_request.status = 'denied'
    elif response == 'alter' or response == 'change':
        new_request = DateRequest(
            sender_id=session['user_id'],
            receiver_id=date_request.sender_id if date_request.receiver_id == session['user_id'] else date_request.receiver_id,
            date=datetime.strptime(new_date, '%Y-%m-%d').date(),
            time=datetime.strptime(new_time, '%H:%M').time(),
            place=new_place,
            status='pending',
            parent_request_id=request_id
        )
        db.session.add(new_request)
        date_request.status = 'altered'

    try:
        db.session.commit()
        return jsonify({'message': 'Response submitted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in respond_to_date_request: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.route('/user_dates')
def user_dates():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    user_id = session['user_id']
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
def blind_dates():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    
    filters = {
        'branch': request.args.get('branch'),
        'year': request.args.get('year'),
        'sleep_schedule': request.args.get('sleep_schedule'),
        'personality_type': request.args.get('personality_type'),
        'ideal_weekend': request.args.get('ideal_weekend'),
        'favorite_sports': request.args.get('favorite_sports'),
        'societies': request.args.get('societies'),
        'leisure_activities': request.args.get('leisure_activities'),
        'music_taste': request.args.get('music_taste'),
        'gender': request.args.get('gender'),  # Add this line
    }
    
    query = User.query.filter(User.id != session['user_id'])
    
    for key, value in filters.items():
        if value:
            if key in ['societies', 'favorite_sports']:
                query = query.filter(getattr(User, key).like(f'%{value}%'))
            else:
                query = query.filter(getattr(User, key) == value)
    
    all_users = query.all()
    return render_template('blind_dates.html', users=all_users)

@app.route('/api/users')
def api_users():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    search_query = request.args.get('search', '')
    filters = {
        'year': request.args.get('year'),
        'ideal_weekend': request.args.get('ideal_weekend'),
        'music_taste': request.args.get('music_taste'),
        'societies': request.args.get('societies'),
        'favorite_sports': request.args.get('favorite_sports'),
        'leisure_activities': request.args.get('leisure_activities'),
        'personality_type': request.args.get('personality_type'),
        'sleep_schedule': request.args.get('sleep_schedule'),
        'aspirations': request.args.get('aspirations'),
        'gender': request.args.get('gender'),  # Add this line
    }
    
    query = User.query.filter(User.id != session['user_id'])
    
    if search_query:
        query = query.filter(User.name.ilike(f'%{search_query}%'))
    
    for key, value in filters.items():
        if value:
            if key in ['societies', 'favorite_sports']:
                query = query.filter(getattr(User, key).like(f'%{value}%'))
            else:
                query = query.filter(getattr(User, key) == value)
    
    users = query.all()
    user_list = [{
        'id': user.id,
        'name': user.name,
        'branch': user.branch,
        'year': user.year,
        'image': user.image,
        'personality_type': user.personality_type,
        'music_taste': user.music_taste,
        'sleep_schedule': user.sleep_schedule,
        'aspirations': user.aspirations,
        'dream_date': user.dream_date,
        'gender': user.gender,  # Add this line
    } for user in users]
    
    return jsonify(user_list)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Update user fields
        user.name = request.form.get('name', user.name)
        user.bio = request.form.get('bio', user.bio)
        user.hobbies = request.form.get('hobbies', user.hobbies)
        user.insta_id = request.form.get('insta_id', user.insta_id)
        user.ideal_weekend = request.form.get('ideal_weekend', user.ideal_weekend)
        user.music_taste = request.form.get('music_taste', user.music_taste)
        user.dream_date = request.form.get('dream_date', user.dream_date)
        user.sleep_schedule = request.form.get('sleep_schedule', user.sleep_schedule)
        user.aspirations = request.form.get('aspirations', user.aspirations)
        user.personality_type = request.form.get('personality_type', user.personality_type)
        user.communication_style = request.form.get('communication_style', user.communication_style) # Added lines to update personality type and communication style
        user.state = request.form.get('state', user.state) #Added to update state
        user.relationship_looking_for = request.form.get('relationship_looking_for', user.relationship_looking_for) #Added to update relationship_looking_for
        cgpa = request.form.get('cgpa') #Added to update cgpa
        if cgpa:
            user.cgpa = float(cgpa)
        else:
            user.cgpa = None

        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/confessions')
def confessions():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    confessions = Confession.query.order_by(Confession.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # Get liked confessions for current user
    liked_confessions = set()
    if 'user_id' in session:
        likes = ConfessionLike.query.filter_by(user_id=session['user_id']).all()
        liked_confessions = {like.confession_id for like in likes}
    
    return render_template('confessions.html', 
                         confessions=confessions, 
                         liked_confessions=liked_confessions)

@app.route('/submit_confession', methods=['POST'])
def submit_confession():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    content = request.form.get('content')
    is_anonymous = request.form.get('is_anonymous') == 'on'
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    author = None if is_anonymous else user.name
    gender = user.gender

    new_confession = Confession(
        content=content,
        author=author,
        gender=gender,
        is_anonymous=is_anonymous
    )
    db.session.add(new_confession)
    db.session.commit()

    return redirect(url_for('confessions'))

@app.route('/like_confession/<int:confession_id>', methods=['POST'])
def like_confession(confession_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Please login to like confessions'}), 401
        
    user_id = session['user_id']
    confession = Confession.query.get_or_404(confession_id)
    
    # Check if user already liked this confession
    existing_like = ConfessionLike.query.filter_by(
        user_id=user_id,
        confession_id=confession_id
    ).first()
    
    if existing_like:
        # Unlike the confession
        db.session.delete(existing_like)
        confession.likes -= 1
    else:
        # Like the confession
        new_like = ConfessionLike(user_id=user_id, confession_id=confession_id)
        db.session.add(new_like)
        confession.likes += 1
    
    db.session.commit()
    return jsonify({
        'likes': confession.likes,
        'liked': not existing_like
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

