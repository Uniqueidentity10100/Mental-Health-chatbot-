from flask import Flask, render_template, request, redirect, session, jsonify, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from textblob import TextBlob
import pandas as pd
import os
import csv
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'space_secret'
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_data')
os.makedirs(DATA_DIR, exist_ok=True)

# Mood-lifting content
JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "What did the meditation app say to the user? Don't worry, be appy!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why did the scarecrow win an award? He was outstanding in his field!",
]

POSITIVE_AFFIRMATIONS = [
    "You're stronger than you know!",
    "Every day is a new opportunity.",
    "You have the power to create change.",
    "Your potential is limitless!",
]

WELLNESS_TIPS = [
    "Try taking a short walk in nature.",
    "Practice deep breathing for 5 minutes.",
    "Listen to your favorite uplifting music.",
    "Call a friend or family member for a chat.",
    "Write down three things you're grateful for.",
    "Try some light stretching or yoga.",
]

# Standardized mood assessment questions based on PHQ-9 and GAD-7
QUESTIONS = [
    {"key": "greeting", 
     "text": lambda username: f"Hi {username}! Let's begin the assessment to understand how you're feeling today."},
    {"key": "age", 
     "text": "First, could you tell me your age?"},
    {"key": "occupation", 
     "text": "What do you do for a living?"},
    {"key": "mood", 
     "text": "How are you feeling today?",
     "options": ["Happy", "Sad", "Depressed"],
     "scores": [0, 2, 4]},
    {"key": "reason", 
     "text": "Can you tell me what's making you feel this way?",
     "condition": lambda data: data.get('mood') in ['Sad', 'Depressed']},
    {"key": "duration", 
     "text": "How long have you been feeling this way?",
     "condition": lambda data: data.get('mood') in ['Sad', 'Depressed'],
     "options": ["Just today", "Few days", "More than a week", "Several weeks"],
     "scores": [1, 2, 3, 4]}
]

# Add remedies dictionary with categories
REMEDIES = {
    "Sad": {
        "Immediate Actions": [
            "Take a short walk in nature",
            "Listen to your favorite uplifting music",
            "Call a friend for a chat",
            "Practice deep breathing exercises"
        ],
        "Daily Practices": [
            "Keep a gratitude journal",
            "Engage in light exercise",
            "Connect with loved ones",
            "Try mindfulness meditation"
        ],
        "Self-Care Tips": [
            "Maintain a regular sleep schedule",
            "Eat nutritious meals",
            "Limit social media use",
            "Spend time in nature"
        ]
    },
    "Depressed": {
        "Professional Help": [
            "Consider talking to a mental health professional",
            "Join a support group or community",
            "Explore therapy options",
            "Consult with your doctor about treatment options"
        ],
        "Daily Structure": [
            "Establish a daily routine",
            "Set small, achievable goals",
            "Take things one step at a time",
            "Create a simple to-do list"
        ],
        "Wellness Activities": [
            "Get some sunlight and fresh air daily",
            "Try gentle exercise like walking or stretching",
            "Practice relaxation techniques",
            "Engage in creative activities you enjoy"
        ],
        "Support System": [
            "Stay connected with supportive friends and family",
            "Join online mental health communities",
            "Share your feelings with trusted people",
            "Don't hesitate to ask for help when needed"
        ]
    }
}

def generate_mood_response(data):
    mood = data.get('mood', '')
    reason = data.get('reason', '')
    
    if mood.lower() in ['sad', 'depressed']:
        mood_remedies = REMEDIES[mood]
        response = [
            f"I'm sorry to hear that {reason} is making you feel {mood.lower()}. It's completely valid to feel this way.",
            "\nHere are some suggestions that might help:"
        ]

        # Add categorized remedies
        for category, remedies in mood_remedies.items():
            response.append(f"\n{category}:")
            # Get 2 random remedies from each category
            selected_remedies = random.sample(remedies, min(2, len(remedies)))
            for remedy in selected_remedies:
                response.append(f"\n• {remedy}")  # Add newline before each bullet point
        
        # Add a supportive message and joke at the end
        response.extend([
            f"\n\nRemember: {random.choice(POSITIVE_AFFIRMATIONS)}",
            f"\nHere's something to lighten your mood:",
            f"\n😊 {random.choice(JOKES)}"  # Add newline before emoji
        ])
        
        return "\n".join(response)
    
    elif mood.lower() == 'happy':
        response = [
            f"It's wonderful that you're feeling {mood.lower()}!",
            f"\nHere are some ways to maintain this positive mood:",
            f"• {random.choice(WELLNESS_TIPS)}",
            f"• Share your happiness with others",
            f"• Document this moment in a journal",
            f"\n{random.choice(POSITIVE_AFFIRMATIONS)}"
        ]
        return "\n".join(response)
    
    return f"Thank you for sharing how you feel! {random.choice(POSITIVE_AFFIRMATIONS)}"

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.route('/')
def index():
    try:
        return redirect('/login')
    except Exception as e:
        print(f"Error in index route: {e}")
        return render_template('error.html', error="An error occurred loading the page"), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            try:
                with open(f'{DATA_DIR}/{username}.txt') as f:
                    stored = f.read().split(',')
                    if check_password_hash(stored[1], password):
                        session['username'] = username
                        # Set username cookie for profile display
                        response = make_response(redirect('/chat'))
                        response.set_cookie('username', username, max_age=86400)  # 24 hours
                        return response
            except:
                pass
            return "Invalid credentials", 401
        return render_template('login.html')
    except Exception as e:
        print(f"Error in login route: {e}")
        return render_template('error.html', error="An error occurred during login"), 500

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        with open(f'{DATA_DIR}/{username}.txt', 'w') as f:
            f.write(f"{username},{password}")
        with open(f'{DATA_DIR}/{username}.csv', 'w') as f:
            f.write("date,assessment_score,mood,message\n")
        # Log in the user directly after signup
        session['username'] = username
        response = make_response(redirect('/chat'))
        response.set_cookie('username', username, max_age=86400)  # 24 hours
        return response
    return render_template('signup.html')

@app.route('/chat')
def chat():
    if "username" not in session:
        return redirect(url_for("login"))
    session['chat_state'] = 0
    session['user_data'] = {}
    session['chat_started'] = False  # Add this line
    return render_template("chatbot.html")

@app.route('/get', methods=["POST"])
def chatbot_reply():
    msg = request.json.get("msg", "").strip()
    is_assessment = request.json.get("isAssessment", False)
    state = session.get("chat_state", 0)
    data = session.get("user_data", {})
    username = session['username']
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Store current response
    if state < len(QUESTIONS):
        question = QUESTIONS[state]
        key = question["key"]
        
        # Validate response based on question type
        if key == "age":
            try:
                age = int(msg)
                if age < 0 or age > 120:
                    return jsonify({
                        "response": "Please enter a valid age between 0 and 120.",
                        "isAssessment": True,
                        "date": current_time,
                        "username": username
                    })
                data[key] = age
            except ValueError:
                return jsonify({
                    "response": "Please enter a valid number for age.",
                    "isAssessment": True,
                    "date": current_time,
                    "username": username
                })
        elif "options" in question and msg not in question["options"]:
            options_str = '", "'.join(question["options"])
            return jsonify({
                "response": f'Please choose one of: "{options_str}"',
                "options": question["options"],
                "isAssessment": True,
                "date": current_time,
                "username": username
            })
        else:
            # Store valid response
            data[key] = msg
            
        # Update session data
        session['user_data'] = data
        session['chat_state'] = state + 1
        
        # Get next question or finish assessment
        if state + 1 >= len(QUESTIONS):
            # Assessment complete - save and generate response
            save_user_data(username, data)
            response = generate_mood_response(data)
            return jsonify({
                "response": response + "\n\nType anything to start a new conversation.",
                "done": True,
                "date": current_time,
                "username": username
            })
        else:
            # Send next question
            next_q = QUESTIONS[state + 1]
            return jsonify({
                "response": next_q["text"],
                "options": next_q.get("options", []),
                "isAssessment": True,
                "questionNumber": state + 1,
                "date": current_time,
                "username": username
            })
    
    return jsonify({
        "response": "Let's start over. How are you feeling today?",
        "isAssessment": True,
        "date": current_time,
        "username": username
    })

# Remove duplicate ASSESSMENT_QUESTIONS array and use ASSESSMENT_FLOW instead
ASSESSMENT_FLOW = [
    {
        "question": lambda username: f"Hi {username}! Let's begin the assessment. First, could you tell me your age?",
        "type": "text",
        "key": "age"
    },
    {
        "question": "What do you do for a living?",
        "type": "text",
        "key": "occupation"
    },
    {
        "question": "How are you feeling today?",
        "type": "mood",
        "key": "mood",
        "options": ["Happy", "Sad", "Depressed"]
    }
]

@app.route('/chat_message', methods=['POST'])
def chat_message():
    if 'username' not in session:
        return jsonify({
            "message": "Please log in first",
            "error": True
        })
    
    data = request.json
    message = data.get('message', '').strip()
    chat_state = data.get('chatState', 'initial')
    user_data = data.get('userData', {})
    username = session['username']
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Initial greeting
    if message == 'start' or chat_state == 'initial':
        return jsonify({
            "message": "Hi! What's your name?",
            "type": "name_question"
        })
    
    # Name collection
    elif chat_state == 'name':
        return jsonify({
            "message": f"Nice to meet you, {message}! Could you tell me your age?",
            "type": "age_question"
        })
    
    # Age validation and collection
    elif chat_state == 'age':
        try:
            age = int(message)
            if 0 <= age <= 120:
                return jsonify({
                    "message": "What is your occupation or designation?",
                    "type": "occupation_question"
                })
            else:
                return jsonify({
                    "message": "Please enter a valid age between 0 and 120.",
                    "type": "age_question"
                })
        except ValueError:
            return jsonify({
                "message": "Please enter a valid number for your age.",
                "type": "age_question"
            })
    
    # Occupation collection
    elif chat_state == 'occupation':
        return jsonify({
            "message": "Have you ever been diagnosed with any mental health condition?",
            "options": ["Yes", "No"],
            "type": "diagnosis_question"
        })
    
    # Past diagnosis collection
    elif chat_state == 'past_diagnosis':
        return jsonify({
            "message": "How are you feeling today?",
            "options": ["Happy", "Sad", "Depressed"],
            "type": "mood_question"
        })
    
    # Mood collection and analysis
    elif chat_state == 'mood':
        # Save user data
        user_data['mood'] = message
        save_user_data(username, user_data)
        
        # Analyze mood
        if message not in ["Happy", "Sad", "Depressed"]:
            mood = analyze_mood(message)
        else:
            mood = message
            
        # Generate response
        response = generate_mood_response({
            'mood': mood,
            'reason': message
        })
        
        # Save mood data
        save_mood_data(username, {
            'mood': mood,
            'reason': message
        })
        
        return jsonify({
            "message": response,
            "type": "mood_response"
        })
    
    # Regular chat
    else:
        mood = analyze_mood(message)
        save_chat_interaction(username, message, mood, 0)
        
        # Check for personal triggers
        personal_triggers = ['friend', 'worthless', 'hurt', 'alone', 'hate']
        if any(word in message.lower() for word in personal_triggers):
            response = [
                "I'm so sorry to hear that you're going through this difficult situation.",
                "It must be really hard feeling this way.",
                "Remember that your worth isn't determined by others' actions.",
                "\nHere are some suggestions that might help:",
                f"• {random.choice(WELLNESS_TIPS)}",
                f"• Talk to someone you trust about how you're feeling",
                f"\n{random.choice(POSITIVE_AFFIRMATIONS)}"
            ]
            bot_response = "\n".join(response)
        else:
            bot_response = generate_response(message, mood)
        
        return jsonify({
            "message": bot_response,
            "type": "chat",
            "mood": mood
        })

@app.route('/logout')
def logout():
    session.clear()
    response = make_response(redirect('/login'))
    response.delete_cookie('username')
    return response

def save_assessment_data(username, data):
    """Save assessment data to user's file"""
    filename = f"{DATA_DIR}/{username}_assessment.csv"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            writer.writerow(["Date", "Age", "Occupation", "Mood"])
        writer.writerow([
            current_time,
            data.get('age', ''),
            data.get('occupation', ''),
            data.get('mood', 'Unknown')
        ])

def save_mood_data(username, assessment_data):
    filename = f"{DATA_DIR}/{username}_mood.csv"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Convert mood to numeric score for visualization
    mood_scores = {
        "Happy": 1,
        "Sad": -1,
        "Depressed": -2,
        "Very Happy": 2,
        "Very Sad": -2,
        "Neutral": 0
    }
    
    mood = assessment_data.get('mood', 'Unknown')
    mood_score = mood_scores.get(mood, 0)
    
    # Create file with headers if it doesn't exist
    file_exists = os.path.exists(filename)
    if not file_exists:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Mood", "Mood_Score", "Reason"])
    
    # Append the new mood data
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            current_time,
            mood,
            mood_score,
            assessment_data.get('reason', '')
        ])

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    mood_file = f"{DATA_DIR}/{username}_mood.csv"
    
    try:
        if os.path.exists(mood_file):
            df = pd.read_csv(mood_file)
            # Convert mood data to format expected by dashboard
            mood_data = []
            
            # Convert mood scores dictionary
            mood_scores = {
                "Happy": 1,
                "Sad": -1,
                "Depressed": -2,
                "Very Happy": 2,
                "Very Sad": -2,
                "Neutral": 0,
                "Unknown": 0
            }
            
            for _, row in df.iterrows():
                mood = row['Mood']  # Column name is capitalized
                mood_data.append({
                    'date': row['Date'],  # Column name is capitalized
                    'mood': mood,
                    'mood_score': mood_scores.get(mood, 0),
                    'reason': str(row.get('Occupation', '')) if pd.notna(row.get('Occupation')) else ''
                })
        else:
            mood_data = []
            
        return render_template('dashboard.html', mood_data=mood_data)
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        import traceback
        print(traceback.format_exc())  # Print detailed error
        return render_template('error.html', error="Error loading mood data")

def save_chat_interaction(username, message, mood, sentiment):
    filename = f"{DATA_DIR}/{username}_chat.csv"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(filename)
    
    # Save mood data for dashboard as well
    if mood in ["Happy", "Sad", "Depressed"]:
        save_mood_data(username, {
            'mood': mood,
            'reason': message
        })
    
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "message_type", "message", "mood"])
        writer.writerow([
            current_time,
            "user",
            message,
            mood
        ])

def complete_assessment(user_data, username):
    response = generate_mood_response(user_data)
    save_user_data(username, user_data)
    session['chat_state'] = len(QUESTIONS)  # Mark assessment as complete
    return jsonify({
        "response": response,
        "done": True,
        "type": "assessment_complete"
    })

def process_regular_chat(message, username):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Add this line
    result = process_message(message)
    save_chat_interaction(username, message, result.get('mood', 'Unknown'), 0)
    result['date'] = current_time  # Add date to result
    return jsonify(result)

def save_user_data(username, data):
    filename = f"{DATA_DIR}/{username}.csv"
    file_exists = os.path.isfile(filename)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Convert mood to numeric score for visualization
    mood_scores = {
        "Happy": 1,
        "Sad": -1,
        "Depressed": -2,
        "Very Happy": 2,
        "Very Sad": -2,
        "Neutral": 0
    }
    
    mood = data.get('mood', 'Unknown')
    mood_score = mood_scores.get(mood, 0)
    
    # Determine overall state based on mood and past diagnosis
    if mood in ["Happy", "Very Happy"]:
        overall_state = "Positive"
    elif mood in ["Sad", "Very Sad"]:
        overall_state = "Needs Support"
    elif mood == "Depressed":
        overall_state = "Immediate Support Recommended"
    else:
        overall_state = "Needs Assessment"

    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Date", "Name", "Age", "Occupation", "Current_Mood", 
                "Mood_Score", "Past_Diagnosis", "Mood_Reason", "Overall_State"
            ])
        
        writer.writerow([
            current_time,
            data.get("name", ""),
            data.get("age", ""),
            data.get("occupation", ""),
            mood,
            mood_score,
            data.get("pastDiagnosis", ""),
            data.get("moodReason", ""),
            overall_state
        ])

last_bot_message = ""

def analyze_mood(message):
    sentiment = TextBlob(message)
    polarity = sentiment.sentiment.polarity
    
    if polarity > 0.5:
        return "Very Happy"
    elif polarity > 0:
        return "Happy"
    elif polarity == 0:
        return "Neutral"
    elif polarity > -0.5:
        return "Sad"
    else:
        return "Very Sad"

def generate_response(message, mood):
    if mood == "Very Happy":
        return f"That's wonderful! {random.choice(POSITIVE_AFFIRMATIONS)}"
    elif mood == "Happy":
        return f"I'm glad you're feeling good! {random.choice(WELLNESS_TIPS)}"
    elif mood == "Neutral":
        return f"I understand. Remember, {random.choice(POSITIVE_AFFIRMATIONS)}"
    elif mood == "Sad":
        return f"I hear you're having a tough time. {random.choice(WELLNESS_TIPS)}"
    else:
        return "I'm here to support you. Would you like to talk about what's troubling you?"

def process_message(message):
    global last_bot_message
    
    # Check if this is the initial name question
    if last_bot_message and "What's your name?" in last_bot_message:
        response = f"Nice to meet you, {message}! How are you feeling today?"
        last_bot_message = response
        return {
            'type': 'name_response',
            'message': response,
            'options': ['Happy', 'Sad', 'Depressed']
        }
    
    # Regular mood processing
    mood = analyze_mood(message)
    response = generate_response(message, mood)
    last_bot_message = response
    return {
        'type': 'mood',
        'message': response,
        'mood': mood
    }

@app.route('/get_user_info')
def get_user_info():
    if 'username' in session:
        return jsonify({'username': session['username']})
    return jsonify({'username': 'Guest'})

@app.route('/get_daily_quote')
def get_daily_quote():
    quotes = [
        "Every day is a new beginning.",
        "You are stronger than you know.",
        "Take it one step at a time.",
        "Your mental health matters.",
        "It's okay to take a break."
    ]
    return jsonify({'quote': random.choice(quotes)})

if __name__ == '__main__':
    app.run(debug=True)
