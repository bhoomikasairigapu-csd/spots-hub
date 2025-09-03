from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import json
import sqlite3
import hashlib

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Contact messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sports scores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport TEXT NOT NULL,
            team1 TEXT NOT NULL,
            team2 TEXT NOT NULL,
            score1 INTEGER NOT NULL,
            score2 INTEGER NOT NULL,
            status TEXT NOT NULL,
            match_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # News table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            excerpt TEXT NOT NULL,
            content TEXT,
            author TEXT DEFAULT 'SportsCentral',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample data
    sample_scores = [
        ('Football', 'Manchester United', 'Liverpool', 2, 1, 'LIVE'),
        ('Basketball', 'Lakers', 'Warriors', 98, 102, 'LIVE'),
        ('Tennis', 'Djokovic', 'Nadal', 6, 4, 'LIVE'),
        ('Cricket', 'India', 'Australia', 245, 189, 'FINISHED'),
        ('Hockey', 'Rangers', 'Bruins', 3, 2, 'LIVE'),
        ('Baseball', 'Yankees', 'Red Sox', 7, 4, 'FINISHED')
    ]
    
    sample_news = [
        ('Major Transfer News Shakes Football World', 
         'A surprise transfer has sent shockwaves through the football community as one of the biggest stars moves to a rival team.',
         'In a stunning turn of events, the football world was left speechless when the announcement came through social media...'),
        
        ('Championship Final Set for Next Week', 
         'Two powerhouse teams prepare for the ultimate showdown in what promises to be the match of the century.',
         'The stage is set for an epic battle as both teams have shown exceptional form throughout the season...'),
        
        ('Record Breaking Performance in Olympics', 
         'Athlete sets new world record in stunning display of human achievement and dedication.',
         'The crowd erupted as the athlete crossed the finish line, breaking a record that had stood for over a decade...'),
        
        ('New Stadium Opens to Fanfare', 
         'State-of-the-art facility welcomes first match with thousands of excited fans in attendance.',
         'The new stadium represents the future of sports entertainment with cutting-edge technology...'),
        
        ('Injury Update on Star Player', 
         'Medical team provides optimistic outlook for the return of the beloved team captain.',
         'Fans can breathe a sigh of relief as the medical report shows positive signs of recovery...'),
        
        ('Youth Academy Produces Next Generation', 
         'Young talents show promise for future as they graduate from the prestigious academy program.',
         'The academy has once again proven its worth by developing exceptional young athletes...')
    ]
    
    # Insert sample data if not exists
    cursor.execute('SELECT COUNT(*) FROM scores')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO scores (sport, team1, team2, score1, score2, status) VALUES (?, ?, ?, ?, ?, ?)', sample_scores)
    
    cursor.execute('SELECT COUNT(*) FROM news')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO news (title, excerpt, content) VALUES (?, ?, ?)', sample_news)
    
    # Create demo user
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = "demo"')
    if cursor.fetchone()[0] == 0:
        password_hash = hashlib.sha256('demo123'.encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)', 
                      ('demo', password_hash, 'demo@sportscentral.com'))
    
    conn.commit()
    conn.close()

# Mock data for real-time updates
sports_updates = [
    'GOAL! Manchester United scores the opening goal against Liverpool!',
    'Lakers trail by 4 points in the final quarter against Warriors',
    'Djokovic wins the first set 6-4 against Nadal in the championship final',
    'Cricket match: India posts a massive total of 245 runs',
    'Rangers take the lead with a power play goal',
    'Yankees extend their lead with a home run in the 7th inning',
    'Breaking: Star player cleared to play in upcoming championship',
    'Weather delay affects outdoor matches in the eastern division',
    'New signing makes debut appearance in today\'s fixture',
    'Referee controversy sparks debate in social media',
    'Transfer window sees unprecedented activity',
    'Young talent breaks into first team squad',
    'Stadium renovation project reaches milestone',
    'Fan favorite announces retirement plans',
    'Coach expresses confidence ahead of big match'
]

# API Routes

@app.route('/')
def home():
    return render_template_string(open('index.html', 'r').read() if os.path.exists('index.html') else 
                                '<h1>Sports API Backend Running</h1><p>API endpoints available at /api/</p>')

@app.route('/api/scores')
def get_scores():
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    cursor.execute('SELECT sport, team1, team2, score1, score2, status FROM scores ORDER BY id DESC')
    scores = cursor.fetchall()
    conn.close()
    
    scores_list = [
        {
            'sport': score[0],
            'team1': score[1],
            'team2': score[2],
            'score1': score[3],
            'score2': score[4],
            'status': score[5]
        }
        for score in scores
    ]
    
    return jsonify({'scores': scores_list})

@app.route('/api/news')
def get_news():
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title, excerpt, content, author, created_at FROM news ORDER BY created_at DESC')
    news = cursor.fetchall()
    conn.close()
    
    news_list = [
        {
            'title': article[0],
            'excerpt': article[1],
            'content': article[2],
            'author': article[3],
            'time': article[4]
        }
        for article in news
    ]
    
    return jsonify({'news': news_list})

@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    
    # Get various statistics
    cursor.execute('SELECT COUNT(*) FROM scores')
    total_games = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM scores WHERE status = "LIVE"')
    live_matches = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM news')
    news_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    conn.close()
    
    stats = [
        {'label': 'Total Games Today', 'value': str(total_games)},
        {'label': 'Live Matches', 'value': str(live_matches)},
        {'label': 'Active Users', 'value': f'{user_count * 1000 + random.randint(100, 999)}'},
        {'label': 'News Articles', 'value': str(news_count)}
    ]
    
    return jsonify({'stats': stats})

@app.route('/api/updates')
def get_updates():
    # Generate random updates with timestamps
    updates = []
    for i in range(10):
        update_time = datetime.now() - timedelta(minutes=random.randint(1, 120))
        updates.append({
            'text': random.choice(sports_updates),
            'time': update_time.strftime('%H:%M:%S'),
            'timestamp': update_time.isoformat()
        })
    
    # Sort by timestamp (newest first)
    updates.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify({'updates': updates})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('SELECT username, email FROM users WHERE username = ? AND password_hash = ?', 
                  (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'success': True,
            'username': user[0],
            'email': user[1],
            'message': 'Login successful'
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Username already exists'}), 409
    
    # Create new user
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute('INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)', 
                      (username, password_hash, email))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Registration successful'})
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    subject = data.get('subject')
    message = data.get('message')
    
    if not all([name, email, subject, message]):
        return jsonify({'error': 'All fields are required'}), 400
    
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO contact_messages (name, email, subject, message) VALUES (?, ?, ?, ?)', 
                      (name, email, subject, message))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Message sent successfully'})
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Failed to send message'}), 500

@app.route('/api/add_score', methods=['POST'])
def add_score():
    data = request.get_json()
    sport = data.get('sport')
    team1 = data.get('team1')
    team2 = data.get('team2')
    score1 = data.get('score1')
    score2 = data.get('score2')
    status = data.get('status', 'LIVE')
    
    if not all([sport, team1, team2, score1 is not None, score2 is not None]):
        return jsonify({'error': 'All fields are required'}), 400
    
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO scores (sport, team1, team2, score1, score2, status) VALUES (?, ?, ?, ?, ?, ?)', 
                      (sport, team1, team2, score1, score2, status))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Score added successfully'})
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Failed to add score'}), 500

@app.route('/api/add_news', methods=['POST'])
def add_news():
    data = request.get_json()
    title = data.get('title')
    excerpt = data.get('excerpt')
    content = data.get('content')
    author = data.get('author', 'SportsCentral')
    
    if not all([title, excerpt]):
        return jsonify({'error': 'Title and excerpt are required'}), 400
    
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO news (title, excerpt, content, author) VALUES (?, ?, ?, ?)', 
                      (title, excerpt, content, author))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'News added successfully'})
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Failed to add news'}), 500

@app.route('/api/random_update')
def get_random_update():
    update = {
        'text': random.choice(sports_updates),
        'time': datetime.now().strftime('%H:%M:%S'),
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(update)

# Admin endpoints (in a real application, these would require authentication)
@app.route('/api/admin/messages')
def get_contact_messages():
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, email, subject, message, created_at FROM contact_messages ORDER BY created_at DESC')
    messages = cursor.fetchall()
    conn.close()
    
    messages_list = [
        {
            'name': msg[0],
            'email': msg[1],
            'subject': msg[2],
            'message': msg[3],
            'created_at': msg[4]
        }
        for msg in messages
    ]
    
    return jsonify({'messages': messages_list})

@app.route('/api/admin/users')
def get_users():
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, email, created_at FROM users ORDER BY created_at DESC')
    users = cursor.fetchall()
    conn.close()
    
    users_list = [
        {
            'username': user[0],
            'email': user[1],
            'created_at': user[2]
        }
        for user in users
    ]
    
    return jsonify({'users': users_list})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    import os
    init_db()
    print("🏈 Sports API Backend Starting...")
    print("📊 Database initialized with sample data")
    print("🌐 API endpoints available:")
    print("   GET  /api/scores - Get live scores")
    print("   GET  /api/news - Get latest news")
    print("   GET  /api/stats - Get statistics")
    print("   GET  /api/updates - Get random updates")
    print("   POST /api/login - User login")
    print("   POST /api/register - User registration")
    print("   POST /api/contact - Send contact message")
    print("   POST /api/add_score - Add new score")
    print("   POST /api/add_news - Add news article")
    print("   GET  /api/random_update - Get single random update")
    print("🔧 Admin endpoints:")
    print("   GET  /api/admin/messages - View contact messages")
    print("   GET  /api/admin/users - View registered users")
    print("\n✅ Server running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)