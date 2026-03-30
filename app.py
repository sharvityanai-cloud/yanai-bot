from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json, os
from datetime import date

app = Flask(__name__)

TASKS_FILE = 'tasks.json'
MEETINGS_FILE = 'meetings.json'
WORKOUTS_FILE = 'workouts.json'

def load_data(f):
    return json.load(open(f, encoding='utf-8')) if os.path.exists(f) else []

def save_data(f, d):
    json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

def add_task(text):
    t = load_data(TASKS_FILE)
    t.append({'id': len(t)+1, 'text': text, 'date': str(date.today()), 'status': 'פתוח'})
    save_data(TASKS_FILE, t)
    return f"✅ משימה נוספה: {text}"

def list_tasks():
    t = [x for x in load_data(TASKS_FILE) if x['status'] == 'פתוח']
    if not t: return "🎉 אין משימות פתוחות!"
    return "📋 *משימות:*\n" + "\n".join(f"{x['id']}. {x['text']}" for x in t)

def complete_task(tid):
    t = load_data(TASKS_FILE)
    for x in t:
        if x['id'] == int(tid):
            x['status'] = 'הושלם'
            save_data(TASKS_FILE, t)
            return f"✅ משימה {tid} הושלמה!"
    return f"❌ לא נמצאה משימה {tid}"

def add_meeting(name, mdate, mtime):
    m = load_data(MEETINGS_FILE)
    m.append({'id': len(m)+1, 'text': name, 'date': mdate, 'time': mtime})
    save_data(MEETINGS_FILE, m)
    return f"📅 פגישה נוספה: {name} ב-{mdate} בשעה {mtime}"

def list_meetings():
    m = load_data(MEETINGS_FILE)
    if not m: return "📅 אין פגישות."
    return "📅 *פגישות:*\n" + "\n".join(f"{x['id']}. {x['text']} — {x['date']} {x['time']}" for x in m)

def add_workout(wtype, notes=''):
    w = load_data(WORKOUTS_FILE)
    w.append({'id': len(w)+1, 'type': wtype, 'date': str(date.today()), 'notes': notes})
    save_data(WORKOUTS_FILE, w)
    return f"💪 אימון נרשם: {wtype}!"

def summary():
    t = load_data(TASKS_FILE)
    w = load_data(WORKOUTS_FILE)
    m = load_data(MEETINGS_FILE)
    done = len([x for x in t if x['status'] == 'הושלם'])
    open_t = len([x for x in t if x['status'] == 'פתוח'])
    return f"📊 *סיכום שבועי:*\n✅ הושלם: {done}\n📋 פתוח: {open_t}\n💪 אימונים: {len(w)}\n📅 פגישות: {len(m)}"

def handle(msg):
    msg = msg.strip()
    if msg.startswith('משימה '): return add_task(msg[6:])
    if msg == 'משימות': return list_tasks()
    if msg.startswith('הושלם '): return complete_task(msg.split()[1])
    if msg.startswith('פגישה '):
        p = msg.split()
        if len(p) >= 4: return add_meeting(' '.join(p[1:-2]), p[-2], p[-1])
        return "❓ פורמט: פגישה [שם] [DD/MM] [HH:MM]"
    if msg == 'פגישות': return list_meetings()
    if msg.startswith('אימון '): 
        p = msg.split(' ', 2)
        return add_workout(p[1], p[2] if len(p)>2 else '')
    if msg == 'סיכום': return summary()
    if msg in ['עזרה','help']:
        return "🤖 *פקודות:*\n• משימה [טקסט]\n• משימות\n• הושלם [מספר]\n• פגישה [שם] [DD/MM] [HH:MM]\n• פגישות\n• אימון [סוג]\n• סיכום"
    return "❓ שלח *עזרה* לרשימת הפקודות."

@app.route('/webhook', methods=['POST'])
def webhook():
    resp = MessagingResponse()
    resp.message(handle(request.values.get('Body', '')))
    return str(resp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
