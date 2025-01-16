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
    hobbies = db.Column(db.String(255))
    bio = db.Column(db.Text)
    image = db.Column(db.String(255))
    previous_relationships = db.Column(db.Integer, default=0)
    previous_dates = db.Column(db.Integer, default=0)
    insta_id = db.Column(db.String(100))
    pet_preference = db.Column(db.String(50))
    sleep_schedule = db.Column(db.String(50))
    life_approach = db.Column(db.String(50))
    personality_type = db.Column(db.String(50))
    beverage_preference = db.Column(db.String(50))
    ideal_weekend = db.Column(db.String(50))
    vacation_style = db.Column(db.String(50))
    music_taste = db.Column(db.String(50))
    sunday_activity = db.Column(db.String(50))
    love_language = db.Column(db.String(50))
    planning_style = db.Column(db.String(50))
    dream_date = db.Column(db.String(50))
    living_preference = db.Column(db.String(50))
    communication_style = db.Column(db.String(50))
    motivation_factor = db.Column(db.String(50))

class DateRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    place = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, denied, altered
    parent_request_id = db.Column(db.Integer, db.ForeignKey('date_request.id'))
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_requests')
    parent_request = db.relationship('DateRequest', remote_side=[id], backref='child_requests')

@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('dashboard.html')
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        gender = request.form['gender']
        branch = request.form['branch']
        year = request.form['year']
        hobbies = request.form['hobbies']
        bio = request.form['bio']
        previous_relationships = request.form['previous_relationships']
        previous_dates = request.form['previous_dates']
        insta_id = request.form['insta_id']
        pet_preference = request.form['pet_preference']
        sleep_schedule = request.form['sleep_schedule']
        life_approach = request.form['life_approach']
        personality_type = request.form['personality_type']
        beverage_preference = request.form['beverage_preference']
        ideal_weekend = request.form['ideal_weekend']
        vacation_style = request.form['vacation_style']
        music_taste = request.form['music_taste']
        sunday_activity = request.form['sunday_activity']
        love_language = request.form['love_language']
        planning_style = request.form['planning_style']
        dream_date = request.form['dream_date']
        living_preference = request.form['living_preference']
        communication_style = request.form['communication_style']
        motivation_factor = request.form['motivation_factor']

        if not re.match(r'[\w\.-]+@iitbbs\.ac\.in$', email):
            return jsonify({'error': 'Invalid email domain. Use iitbbs.ac.in email.'}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(
            email=email, password=hashed_password, name=name, gender=gender,
            branch=branch, year=year, hobbies=hobbies, bio=bio,
            previous_relationships=previous_relationships,
            previous_dates=previous_dates, insta_id=insta_id,
            pet_preference=pet_preference, sleep_schedule=sleep_schedule,
            life_approach=life_approach, personality_type=personality_type,
            beverage_preference=beverage_preference, ideal_weekend=ideal_weekend,
            vacation_style=vacation_style, music_taste=music_taste,
            sunday_activity=sunday_activity, love_language=love_language,
            planning_style=planning_style, dream_date=dream_date,
            living_preference=living_preference, communication_style=communication_style,
            motivation_factor=motivation_factor
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
            return jsonify({'message': 'Signin successful'}), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 400

    return render_template('signin.html')

@app.route('/signout')
def signout():
    session.pop('user_id', None)
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
        'pet_preference': request.args.get('pet_preference'),
        'sleep_schedule': request.args.get('sleep_schedule'),
        # Add more filters here
    }
    
    query = User.query.filter(User.id != session['user_id'])
    
    if search_query:
        query = query.filter(User.name.ilike(f'%{search_query}%'))
    
    for key, value in filters.items():
        if value:
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
            'hobbies': user.hobbies,
            'bio': user.bio,
            'image': user.image,
            'insta_id': user.insta_id,
            'pet_preference': user.pet_preference,
            'sleep_schedule': user.sleep_schedule,
            'life_approach': user.life_approach,
            'personality_type': user.personality_type,
            'beverage_preference': user.beverage_preference,
            'ideal_weekend': user.ideal_weekend,
            'vacation_style': user.vacation_style,
            'music_taste': user.music_taste,
            'sunday_activity': user.sunday_activity,
            'love_language': user.love_language,
            'planning_style': user.planning_style,
            'dream_date': user.dream_date,
            'living_preference': user.living_preference,
            'communication_style': user.communication_style,
            'motivation_factor': user.motivation_factor
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
            place=place
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
    all_users = User.query.filter(User.id != session['user_id']).all()
    return render_template('blind_dates.html', users=all_users)

@app.route('/api/users')
def api_users():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    search_query = request.args.get('search', '')
    filters = {
        'pet_preference': request.args.get('pet_preference'),
        'sleep_schedule': request.args.get('sleep_schedule'),
        # Add more filters here
    }
    
    query = User.query.filter(User.id != session['user_id'])
    
    if search_query:
        query = query.filter(User.name.ilike(f'%{search_query}%'))
    
    for key, value in filters.items():
        if value:
            query = query.filter(getattr(User, key) == value)
    
    users = query.all()
    user_list = [{
        'id': user.id,
        'name': user.name,
        'branch': user.branch,
        'year': user.year,
        'image': user.image
    } for user in users]
    
    return jsonify(user_list)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

