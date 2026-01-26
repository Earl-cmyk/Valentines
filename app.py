# app.py
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import secrets
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///valentine.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Models
class ValentineResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    girlfriend_name = db.Column(db.String(100), nullable=False)
    response = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))


class LoveNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_secret = db.Column(db.Boolean, default=False)


class Memory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    memory_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50))  # first_meet, date, trip, etc.


# Create tables
with app.app_context():
    db.create_all()

    # Add some default love notes if empty
    if LoveNote.query.count() == 0:
        default_notes = [
            LoveNote(
                title="Why I Love You",
                content="Every moment with you feels like a beautiful dream. Your smile lights up my world and your laughter is my favorite sound. I love the way you make ordinary moments feel extraordinary and how you understand me like no one else ever has.",
                is_secret=False
            ),
            LoveNote(
                title="The Way You Make Me Feel",
                content="With you, I feel completely myself - accepted, cherished, and loved. You've shown me what true happiness feels like, and every day I'm grateful that our paths crossed.",
                is_secret=False
            ),
            LoveNote(
                title="August 10 - The Beginning",
                content="I'll never forget August 10th - the day we both admitted there was something special between us. My heart raced with excitement and hope, knowing this was the start of something beautiful. That moment changed everything for me.",
                is_secret=False
            ),
            LoveNote(
                title="September 14 - Love Confirmed",
                content="When we said 'I love you' on September 14th, it felt like my heart found its home. Those three words have meant more each time we've said them, growing deeper and truer with every passing day.",
                is_secret=False
            ),
            LoveNote(
                title="Every Monthsary With You",
                content="Each 14th of the month is a celebration of us. I'm endlessly grateful for every day we've shared, every challenge we've overcome together, and every moment of joy you've brought into my life. Here's to all the monthsaries to come!",
                is_secret=False
            ),
            LoveNote(
                title="My Favorite Things About You",
                content="Your kindness that knows no bounds, your laughter that brightens any room, your patience when I need it most, your intelligence that constantly inspires me, and the way you love me - completely and unconditionally.",
                is_secret=False
            ),
            LoveNote(
                title="Our First Valentine's Together",
                content="Celebrating our first Valentine's Day as a couple feels like a dream come true. You're the love I've always hoped for, and I can't wait to make this day as special as you are to me. This is just the first of many Valentine's we'll celebrate together.",
                is_secret=False
            ),
            LoveNote(
                title="My Promise to You",
                content="I promise to love you more each day than I did the day before. I promise to be your safe place, your biggest supporter, and your partner in all things. I promise to cherish every moment with you and to always choose us.",
                is_secret=False
            )
        ]
        db.session.add_all(default_notes)
        db.session.commit()

    # Add some default memories if empty
    if Memory.query.count() == 0:
        default_memories = [
            Memory(
                title="The Beginning of Us",
                description="August 10 - The day we first acknowledged that something special was growing between us. I remember the butterflies, the hope, and the beautiful realization that this was the start of our love story.",
                memory_date=datetime(datetime.now().year, 8, 10),
                category="beginning"
            ),
            Memory(
                title="Love Confirmed",
                description="September 14 - The day we officially confessed our love for each other. Saying 'I love you' felt natural yet revolutionary, changing everything in the most beautiful way.",
                memory_date=datetime(datetime.now().year, 9, 14),
                category="milestone"
            ),
            Memory(
                title="One Month Together",
                description="October 14 - Our first monthsary! One month of official love that already felt like forever. You had become my favorite part of every day.",
                memory_date=datetime(datetime.now().year, 10, 14),
                category="monthsary"
            ),
            Memory(
                title="Two Months of Bliss",
                description="November 14 - Two months with you and my gratitude only grew deeper. Thankful for your patience, understanding, and the joy of building something real together.",
                memory_date=datetime(datetime.now().year, 11, 14),
                category="monthsary"
            ),
            Memory(
                title="Three Months Stronger",
                description="December 14 - Three months in, and our love felt both comfortable and exciting. Celebrating our love during the holidays made everything feel magical.",
                memory_date=datetime(datetime.now().year, 12, 14),
                category="monthsary"
            ),
            Memory(
                title="Four Months of Growth",
                description="January 14 - Starting a new year with you by my side was the greatest gift. Four months together and grateful for every lesson learned and every moment of pure happiness.",
                memory_date=datetime(datetime.now().year + 1, 1, 14),
                category="monthsary"
            ),
            Memory(
                title="Five Months & First Valentine's",
                description="February 14 - Five months together and our first Valentine's Day! The perfect celebration of our love. You've made every day since August 10 feel like a celebration of true connection.",
                memory_date=datetime(datetime.now().year + 1, 2, 14),
                category="valentine"
            ),
            Memory(
                title="Our Future Together",
                description="Every 14th to come - Each monthsary is a reminder of how blessed I am to have you. No matter how many months pass, my gratitude only deepens. Here's to all our future celebrations.",
                memory_date=None,  # No specific date for future memories
                category="future"
            )
        ]
        db.session.add_all(default_memories)
        db.session.commit()

# Routes
@app.route('/')
def home():
    """Main invitation page"""
    return render_template('invitation.html')


@app.route('/api/valentine-response', methods=['POST'])
def valentine_response():
    """Handle the Valentine's response"""
    try:
        data = request.json
        response = ValentineResponse(
            girlfriend_name=data.get('name', 'My Love'),
            response=data.get('response'),
            message=data.get('message', ''),
            ip_address=request.remote_addr
        )
        db.session.add(response)
        db.session.commit()

        # Store in session for personalized experience
        session['girlfriend_name'] = data.get('name', 'My Love')
        session['said_yes'] = (data.get('response') == 'yes')

        return jsonify({
            'success': True,
            'message': 'Response saved! You made me so happy!' if data.get('response') == 'yes' else 'Response saved!'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/love-notes')
def love_notes():
    """Page with love notes"""
    notes = LoveNote.query.filter_by(is_secret=False).order_by(LoveNote.created_at.desc()).all()
    return render_template('love_notes.html', notes=notes)


@app.route('/api/love-notes', methods=['GET', 'POST'])
def api_love_notes():
    """API for love notes"""
    if request.method == 'POST':
        try:
            data = request.json
            note = LoveNote(
                title=data.get('title'),
                content=data.get('content'),
                is_secret=data.get('is_secret', False)
            )
            db.session.add(note)
            db.session.commit()
            return jsonify({'success': True, 'id': note.id})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    else:
        notes = LoveNote.query.filter_by(is_secret=False).order_by(LoveNote.created_at.desc()).all()
        return jsonify([{
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at.strftime('%B %d, %Y')
        } for note in notes])


@app.route('/memories')
def memories():
    """Page with shared memories"""
    memories_list = Memory.query.order_by(Memory.memory_date.desc()).all()
    return render_template('memories.html', memories=memories_list)


@app.route('/api/memories', methods=['GET', 'POST'])
def api_memories():
    """API for memories"""
    if request.method == 'POST':
        try:
            data = request.json
            memory = Memory(
                title=data.get('title'),
                description=data.get('description'),
                category=data.get('category', 'special'),
                memory_date=datetime.strptime(data.get('memory_date'), '%Y-%m-%d') if data.get(
                    'memory_date') else datetime.utcnow()
            )
            db.session.add(memory)
            db.session.commit()
            return jsonify({'success': True, 'id': memory.id})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    else:
        memories_list = Memory.query.order_by(Memory.memory_date.desc()).all()
        return jsonify([{
            'id': memory.id,
            'title': memory.title,
            'description': memory.description,
            'category': memory.category
        } for memory in memories_list])


@app.route('/secret-note')
def secret_note():
    """A secret page for a special note (password protected)"""
    return render_template('secret_note.html')


@app.route('/api/check-secret', methods=['POST'])
def check_secret():
    """Check secret password"""
    data = request.json
    # You can change this password to something meaningful for you two
    if data.get('password') == 'forever' or data.get('password') == 'valentine':
        secret_note = LoveNote.query.filter_by(is_secret=True).first()
        return jsonify({
            'success': True,
            'note': {
                'title': secret_note.title if secret_note else 'My Secret Love',
                'content': secret_note.content if secret_note else 'I have a lifetime of love to share with you.'
            }
        })
    return jsonify({'success': False, 'error': 'Incorrect password'}), 401


@app.route('/countdown')
def countdown():
    """Valentine's Day countdown page"""
    valentine_date = datetime(datetime.now().year, 2, 14)
    if datetime.now().month > 2 or (datetime.now().month == 2 and datetime.now().day > 14):
        valentine_date = datetime(datetime.now().year + 1, 2, 14)

    days_left = (valentine_date - datetime.now()).days
    return render_template('countdown.html', days_left=days_left, valentine_date=valentine_date)


@app.route('/api/stats')
def get_stats():
    """Get statistics about the invitation"""
    total_responses = ValentineResponse.query.count()
    yes_responses = ValentineResponse.query.filter_by(response='yes').count()

    return jsonify({
        'total_responses': total_responses,
        'yes_responses': yes_responses,
        'response_rate': (yes_responses / total_responses * 100) if total_responses > 0 else 0
    })


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)