from flask import Flask, request, redirect, send_file
import datetime, os
import firebase_admin
from firebase_admin import credentials, firestore
from groq import Groq
from absl import app, logging

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Initialize absl logging
logging.set_verbosity(logging.INFO)
logging.info('Initializing application...')

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate('template/serviceAccountKey.json')
    firebase_admin.initialize_app(
        cred, {
            'databaseURL':
            'https://console.firebase.google.com/project/spacehack-348ab/database/spacehack-348ab-default-rtdb/data/~2F'
        })

# Initialize Firestore
db = firestore.client()


def getChat():
    message = ""
    with open("template/therapist/message.html", "r") as f:
        message = f.read()

    chats_ref = db.collection('chats').order_by(
        'timestamp', direction=firestore.Query.DESCENDING).limit(5)
    docs = chats_ref.stream()

    result = ""
    for doc in docs:
        chat = doc.to_dict()
        myMessage = message
        myMessage = myMessage.replace("{timestamp}", doc.id)
        myMessage = myMessage.replace("{message}", chat["urmessage"])
        myMessage = myMessage.replace("{answer}", chat["Airesponse"])
        result += myMessage

    return result


@app.route('/')
def index():
    with open("template/Main.html", "r") as f:
        page = f.read()
    with open("template/Components/header.html", "r") as f:
        header = f.read()
    with open("template/Components/footer.html", "r") as f:
        footer = f.read()
    page = page.replace("{header}", header)
    page = page.replace("{footer}", footer)

    return page


@app.route('/DrawZone')
def DrawZone():
    with open("template/Draw/DrawZone.html", "r") as f:
        page = f.read()
    with open("template/Components/header.html", "r") as f:
        header = f.read()
    with open("template/Components/footer.html", "r") as f:
        footer = f.read()
    page = page.replace("{header}", header)
    page = page.replace("{footer}", footer)

    return page


@app.route('/Therapist')
def TherapistChat():
    with open("template/therapist/chat.html", "r") as f:
        page = f.read()

    with open("template/Components/header.html", "r") as f:
        header = f.read()

    with open("template/Components/footer.html", "r") as f:
        footer = f.read()

    page = page.replace("{chats}", getChat())
    page = page.replace("{header}", header)
    page = page.replace("{footer}", footer)

    return page


@app.route('/add', methods=["POST"])
def add():
    form = request.form
    urmessage = form["message"]
    date = datetime.datetime.now()
    timestamp = datetime.datetime.timestamp(date)
    prompt = (
        f"You are a therapist and your patient said this {urmessage}, be as short as possible. Answer in the same language the user is using. Your answer must be under 50 words"
    )
    response = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": prompt,
        }],
        model="llama3-8b-8192",
    )

    Airesponse = response.choices[0].message.content
    chat_data = {
        "timestamp": timestamp,
        "urmessage": urmessage,
        "Airesponse": Airesponse
    }

    db.collection('chats').document(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).set(chat_data)

    return redirect("/Therapist")


# Journal Routes #WORKING

@app.route('/past')
def past_entries():
    entries_ref = db.collection('journal').order_by(
        'timestamp', direction=firestore.Query.DESCENDING)
    docs = entries_ref.stream()
    entries = [doc.to_dict() for doc in docs]

    # Read the HTML file content
    with open('templates/journal/past_entries.html', 'r') as file:
        html_content = file.read()

    # Inject the entries data into the HTML content
    entries_html = ''.join([f"<div><h2>{entry['title']}</h2><p>{entry['content']}</p></div>" for entry in entries])
    html_content = html_content.replace('{{ entries }}', entries_html)

    # Save the modified HTML content to a temporary file
    temp_file_path = 'temp/past_entries.html'
    os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(html_content)

    # Send the modified HTML file
    return send_file(temp_file_path)

@app.route('/entry/<entry_id>')
def entry(entry_id):
    entry_ref = db.collection('journal').document(entry_id)
    entry = entry_ref.get().to_dict()

    # Read the HTML file content
    with open('templates/entry.html', 'r') as file:
        html_content = file.read()

    # Inject the entry data into the HTML content
    html_content = html_content.replace('{{ entry.title }}', entry['title'])
    html_content = html_content.replace('{{ entry.content }}', entry['content'])

    # Save the modified HTML content to a temporary file
    temp_file_path = f'temp/entry_{entry_id}.html'
    os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(html_content)

    # Send the modified HTML file
    return send_file(temp_file_path)

# Piano Routes
@app.route('/Music')
def Piano():
    with open("template/piano/piano.html", "r") as f:
        page = f.read()
    return page





if __name__ == '__main__':
    logging.info('Starting Flask app...')
    app.run(host='0.0.0.0', port=5000)
