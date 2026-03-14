from flask import Flask, render_template, request, redirect, url_for, jsonify , session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from textblob import TextBlob
from rapidfuzz import fuzz
import os


app = Flask(__name__)
app.secret_key = "peacebot_secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
def find_best_match(user_message, dataset):

    best_score = 0
    best_response = None

    for question, answer in dataset.items():

        score = fuzz.partial_ratio(user_message, question)

        if score > best_score:
            best_score = score
            best_response = answer

    if best_score > 75:
        return best_response

    return None
    


# ================= DATABASE =================== #

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    dob = db.Column(db.String(20))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    theme = db.Column(db.String(50), default="light")


class SleepTrack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    sleep_time = db.Column(db.String(20))
    wake_time = db.Column(db.String(20))
    mood = db.Column(db.String(20))
    score = db.Column(db.Integer)
    date = db.Column(db.String(20))


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ================= AGE DATASET =================== #

AGE_DATA = {
    "13-18": ["Academic stress sleep disturbance","Late night device usage","Irregular sleep schedule","Anxiety before exams"],
    "19-35": ["Insomnia","Overthinking at night","Stress-related sleep disturbance","Irregular sleep cycle"],
    "36-55": ["Work stress insomnia","Chronic insomnia","Sleep apnea / snoring","Fatigue / burnout"],
    "56+": ["Light or fragmented sleep","Early morning waking","Restless legs syndrome","Circadian rhythm issues"]
}


# ================= SMALL TALK DATASET =================== #

SMALL_TALK_DATASET = {

"hi":"Hello! 🌙 I'm PeaceBot. How has your sleep been recently?",
"hello":"Hi there! 😊 I'm here to help you improve your sleep.",
"hey":"Hey! 👋 How can I assist you today?",
"how are you":"I'm doing great and ready to help you with sleep advice!",
"good morning":"Good morning! ☀️ How was your sleep?",
"good evening":"Good evening! 🌙 Are you preparing for sleep tonight?",
"good night":"Good night! 😴 I hope you have a peaceful sleep.",
"thank you":"You're welcome! I'm always here to help.",
"thanks":"Happy to help! Ask me anything about sleep.",
"who are you":"I'm PeaceBot 🤖, designed to help improve sleep habits.",
"help":"You can ask me about insomnia, sleep tips, or sleep disorders."
}


# ================= ANONYMOUS QA =================== #

ANONYMOUS_QA = {

"how much sleep do i need":"Adults need 7–9 hours of sleep each night.",
"why cant i sleep":"Stress, caffeine, irregular sleep schedule, or phone usage may cause sleep problems.",
"is it bad to sleep late":"Sleeping late regularly can disturb your circadian rhythm.",
"how to fall asleep fast":"Avoid screens before bed, keep lights dim, and practice breathing.",
"why do i wake up at night":"Stress or caffeine intake may disturb sleep.",
"is phone bad before sleep":"Yes, blue light reduces melatonin.",
"can stress affect sleep":"Yes, stress increases cortisol and disturbs sleep.",
"what foods help sleep":"Bananas, almonds, warm milk, oats help sleep.",
"can exercise improve sleep":"Yes, regular exercise improves sleep quality.",
"why do i feel tired after sleeping":"Poor sleep quality or irregular sleep cycles may cause this."
}


# ================= SLEEP DISORDER QA =================== #

SLEEP_DISORDER_QA = {

"why do i wake up at 3 am":"Waking at 3 AM is common during stress or anxiety.",
"why cant i fall asleep even when i am tired":"Overthinking or irregular sleep schedule may cause this.",
"why do i feel sleepy during the day":"Daytime sleepiness may occur due to poor sleep quality.",
"what causes insomnia":"Stress, anxiety, caffeine, or irregular routines.",
"how long does insomnia last":"Short-term insomnia may last a few days to weeks.",
"why do i get nightmares":"Stress, trauma, or medications may cause nightmares.",
"what is sleep apnea":"Sleep apnea is when breathing stops during sleep.",
"how do i stop overthinking at night":"Try journaling or meditation before sleep.",
"why do i feel anxious at night":"Night anxiety often comes from accumulated daily stress."
}

SLEEP_DATASET = {

# GENERAL SLEEP
"why is sleep important": "Sleep is important because it allows the brain and body to recover, improves memory, and supports overall health.",
"why do we need sleep": "Sleep helps the brain process information, repair cells, and restore energy.",
"benefits of sleep": "Good sleep improves concentration, mood, immunity, and overall health.",
"what happens if i dont sleep": "Lack of sleep can cause fatigue, poor concentration, mood swings, and long-term health issues.",
"sleep health": "Healthy sleep improves brain function, emotional well-being, and physical health.",

# SLEEP HOURS
"how many hours should i sleep": "Most adults need between 7 and 9 hours of sleep each night.",
"ideal sleep duration": "The ideal sleep duration for adults is around 7–9 hours.",
"is 6 hours sleep enough": "For most people, 6 hours is slightly low. 7–9 hours is recommended.",
"is 5 hours sleep enough": "Five hours is usually not enough and may cause sleep deprivation.",

# SLEEP SCHEDULE
"how to maintain sleep schedule": "Try going to bed and waking up at the same time every day.",
"why is sleep schedule important": "A regular sleep schedule helps regulate your internal body clock.",
"how to fix sleep schedule": "Gradually adjust your bedtime and wake-up time by 15–30 minutes daily.",
"sleep routine": "A consistent bedtime routine signals the brain that it's time to sleep.",

# INSOMNIA
"what is insomnia": "Insomnia is a sleep disorder where a person has trouble falling or staying asleep.",
"why do i have insomnia": "Insomnia may be caused by stress, anxiety, caffeine, or irregular sleep habits.",
"how to treat insomnia": "Relaxation techniques, a consistent sleep schedule, and reducing screen time can help treat insomnia.",
"can stress cause insomnia": "Yes, stress and anxiety are common causes of insomnia.",
"how long does insomnia last": "Short-term insomnia may last a few days or weeks depending on the cause.",

# NIGHTMARES
"what are nightmares": "Nightmares are disturbing dreams that may wake you from sleep.",
"why do i get nightmares": "Nightmares may occur due to stress, anxiety, trauma, or certain medications.",
"how to stop nightmares": "Maintaining a calm bedtime routine and reducing stress may help reduce nightmares.",
"bad dreams": "Bad dreams can be linked to emotional stress or irregular sleep patterns.",

# NIGHT WAKING
"why do i wake up at night": "Night waking may occur due to stress, anxiety, caffeine, or poor sleep habits.",
"why do i wake up at 3 am": "Waking around 3 AM can happen due to stress or disruptions in sleep cycles.",
"why do i wake up frequently": "Frequent waking may be caused by stress, sleep disorders, or lifestyle factors.",

# FALLING ASLEEP
"why cant i fall asleep": "Difficulty falling asleep may occur due to stress, caffeine, or screen exposure.",
"cant sleep": "Try relaxation techniques like deep breathing and reducing screen exposure before bed.",
"trouble sleeping": "Trouble sleeping may happen due to anxiety, irregular sleep schedules, or lifestyle habits.",

# SLEEP QUALITY
"how to improve sleep quality": "Maintain a regular sleep schedule, avoid caffeine at night, and keep your room quiet and dark.",
"why do i feel tired after sleeping": "Feeling tired after sleep may indicate poor sleep quality or interrupted sleep.",
"how to sleep better": "Try reducing screen exposure before bed and maintaining a relaxing bedtime routine.",

# STRESS
"stress and sleep": "Stress can increase cortisol levels and make it difficult to fall asleep.",
"how stress affects sleep": "Stress activates the brain and can cause insomnia or restless sleep.",
"how to relax before sleep": "Meditation, deep breathing, and reading can help relax your mind before sleep.",

# PHONE USAGE
"phone before sleep": "Using phones before bed exposes you to blue light that reduces melatonin production.",
"is phone bad before sleep": "Yes, blue light from screens can delay sleep.",
"can phone cause insomnia": "Excessive screen time before bed can contribute to insomnia.",

# FOOD
"foods for better sleep": "Bananas, almonds, oats, and warm milk can promote better sleep.",
"what foods help sleep": "Foods rich in magnesium like nuts and bananas may improve sleep.",
"can caffeine affect sleep": "Yes, caffeine can delay sleep and reduce sleep quality.",

# EXERCISE
"exercise and sleep": "Regular exercise can improve sleep quality and reduce stress.",
"can exercise help sleep": "Yes, physical activity helps regulate sleep cycles.",

# ENVIRONMENT
"best environment for sleep": "A cool, dark, and quiet room promotes better sleep.",
"room temperature for sleep": "Around 18–22°C is ideal for comfortable sleep.",
"should bedroom be dark": "Yes, darkness helps the body produce melatonin.",

# DAYTIME SLEEPINESS
"why am i sleepy during the day": "Daytime sleepiness may occur due to poor sleep quality or insufficient sleep.",
"why do i feel tired all day": "Constant tiredness may indicate sleep deprivation.",

# SLEEP CYCLE
"what is sleep cycle": "A sleep cycle lasts about 90 minutes and includes light sleep, deep sleep, and REM sleep.",
"what is rem sleep": "REM sleep is the stage where most dreaming occurs.",

# MENTAL HEALTH
"anxiety at night": "Night anxiety can occur when the brain processes stress from the day.",
"why do i feel anxious at night": "Anxiety may increase at night due to reduced distractions.",

# IMPROVEMENT
"tips for good sleep": "Maintain a consistent sleep schedule, avoid caffeine at night, and create a calm sleeping environment.",
"sleep hygiene": "Sleep hygiene means maintaining habits that support good sleep quality.",
"how to develop healthy sleep habits": "Keep a regular bedtime routine and limit screen exposure before bed."
}
SONGS_PER_PAGE = 5

TAMIL_SONG_LIST = [
    "Pachai Nirame from Alaipayuthey",
    "Munbe Vaa from Sillunu Oru Kaadhal",
    "Nenjukkul Peidhidum from Vaaranam Aayiram",
    "Vaseegara from Minnale",
    "Kangal Irandal from Subramaniapuram",
    "Anbil Avan from Vinnaithaandi Varuvaayaa",
    "Uyire Uyire from Bombay",
    "Enna Solla Pogirai from Kandukondain Kandukondain",
    "New York Nagaram from Sillunu Oru Kaadhal",
    "Poongatrile from Uyire",
    "Aaruyire from Guru",
    "Suttrum Vizhi from Ghajini",
    "Kadhal Rojave from Roja",
    "Nila Kaigirathu from Indira",
    "Thalli Pogathey from Achcham Yenbadhu Madamaiyada",
    "Mun Andhi from 7aum Arivu",
    "Nenjodu Kalandidu from Kaadhal Konden",
    "Vellai Pookal from Kannathil Muthamittal",
    "Snehithane from Alaipayuthey",
    "Ennavale Adi Ennavale from Kadhalan",
    "Kadhal Anukkal from Enthiran",
    "Mannipaaya from Vinnaithaandi Varuvaayaa",
    "Po Nee Po from 3",
    "Moongil Thottam from Kadal",
    "Unakkenna Venum Sollu from Yennai Arindhaal",
    "Nallai Allai from Kaatru Veliyidai",
    "Oru Deivam Thantha Poove from Kannathil Muthamittal",
    "Malargal Kaettaen from OK Kanmani",
    "Pookal Pookum from Madrasapattinam",
    "Idhayathai Yedho Ondru from Yennai Arindhaal",
    "Unnale Unnale from Unnale Unnale",
    "Hosanna from Vinnaithaandi Varuvaayaa",
    "Yaarumilla from Kaaviya Thalaivan",
    "Oru Naalil from Pudhupettai",
    "Mazhai Kuruvi from Chekka Chivantha Vaanam",
    "Thendral Vandhu from Avatharam",
    "Vaan Varuvaan from Kaatru Veliyidai",
    "Kannana Kanne from Viswasam",
    "Maruvaarthai from Enai Noki Paayum Thota",
    "Adiye from Kadal",
    "Nila Nila Odi Vaa from Children's classic lullaby",
    "Chinna Chinna Aasai from Roja",
    "Kaatril Varum Geetham from Johny",
    "Ilaya Nila from Payanangal Mudivathillai",
    "Poove Sempoove from Solla Thudikuthu Manasu",
    "Naan Pizhai from Kaathuvaakula Rendu Kaadhal",
    "Kadhal Sadugudu from Alaipayuthey",
    "Ennamo Yedho from Ko",
    "Vizhigalil Oru Vaanavil from Deiva Thirumagal",
    "Aarariraro from Raam",
"These songs have calm melodies that can help you relax and fall asleep peacefully 🌙"
]

EMPATHY_DATASET = {

# GENERAL SLEEP PROBLEMS
"not sleeping well":"I'm sorry you're going through that 😔. Sleep problems can be really frustrating. Try relaxing before bed and avoiding screens late at night. Small changes can make a big difference. You’ve got this! 🌙",

"cant sleep":"That sounds really difficult 😟. Many people experience this sometimes. Try taking slow deep breaths and calming your mind before bed. Your body will slowly learn to relax.",

"unable to sleep":"I understand how frustrating that can be 😔. Don't worry, you're not alone. Try creating a relaxing bedtime routine like reading or listening to calm music.",

"sleep problem":"I'm really glad you told me about it 💙. Sleep problems happen to many people, especially during stressful times. Let's work together to improve your sleep habits.",

"sleep not good":"I'm sorry your sleep hasn't been good lately 😞. Try maintaining a consistent bedtime and avoiding caffeine in the evening. Small improvements can help a lot.",

# STRESS RELATED
"stress":"Stress can definitely affect sleep 😟. Try relaxing activities like meditation, journaling, or deep breathing before bed. Your mind deserves some peace too.",

"too much stress":"I'm sorry you're feeling so stressed 😔. Remember that taking small breaks and calming your mind can help improve sleep and overall well-being.",

"overthinking":"Overthinking at night happens to many people 😟. Try writing your thoughts in a journal before bed so your mind can relax.",

"thinking too much":"It sounds like your mind is very active at night 😔. Try listening to calm music or practicing deep breathing to help your mind slow down.",

# LATE SLEEP
"sleeping late":"Don't worry, this is very common nowadays 😊. Try slowly adjusting your bedtime by 15 minutes earlier each day.",

"sleep late":"Sleeping late can happen when our routines get disturbed. Start with small changes like dimming lights and avoiding screens before bedtime.",

"cant sleep early":"It's okay, many people struggle with this 😌. Try relaxing activities before bed and gradually shift your sleep time earlier.",

# NIGHT WAKE
"wake up at night":"That must be frustrating 😔. Night waking can happen due to stress or lifestyle habits. Try keeping your room calm and quiet before sleep.",

"wake up 3am":"Waking up around 3 AM happens to many people. It might be related to stress or sleep cycles. Try relaxation breathing and avoid worrying too much.",

# TIRED
"tired all day":"Feeling tired all day can be exhausting 😞. Improving sleep quality slowly will help you regain your energy.",

"sleepy during day":"Daytime sleepiness can happen when sleep quality isn't good. Let's try improving your bedtime routine.",

# NIGHT ANXIETY
"anxious at night":"Night anxiety can feel overwhelming 😟. Try calming activities like meditation or deep breathing before sleep.",

"night anxiety":"I'm sorry you're experiencing that 😔. Remember that your mind needs relaxation after a busy day.",

# MOTIVATIONAL SUPPORT
"i feel bad":"I'm really sorry you're feeling this way 💙. Remember that tough nights don't last forever. Tomorrow is a new opportunity to improve.",

"i am tired of this":"I understand that this can feel exhausting 😔. But small improvements in sleep habits can make a big difference over time.",

"nothing helps":"It may feel that way sometimes 😞, but please don't lose hope. Improving sleep takes patience and small steps.",

# FRIENDLY
"ok":"Alright 😊. If you'd like, tell me more about your sleep habits and I can help you improve them.",

"sure":"Great! I'm here to help you step by step with your sleep improvement journey.",

"hmm":"Take your time 😊. I'm here to listen and help you with any sleep concerns.",

"yes":"That's good to hear! Tell me more about your sleep routine.",

"no":"That's okay 😊. Feel free to tell me what is troubling your sleep.",

# GOOD SLEEP
"slept well":"That's wonderful to hear! 🌙 Good sleep is very important for your health. Keep maintaining those healthy sleep habits.",

"good sleep":"I'm really happy your sleep was good 😊. Maintaining a consistent sleep schedule will help keep it that way.",

# ENCOURAGEMENT
"improve sleep":"That's a great goal! 🌟 Small steps like relaxing before bed and reducing screen time can help you improve sleep.",

"sleep tips":"I'd be happy to help! Try keeping your bedroom dark, avoiding caffeine at night, and maintaining a consistent sleep schedule.",

"help me sleep":"Of course 😊. Let's work together to improve your sleep habits step by step.",

"sleep advice":"Sure! Creating a relaxing bedtime routine and avoiding screens before sleep can really help.",

# MOTIVATION
"feeling low":"I'm really sorry you're feeling low 😔. Remember that taking care of your sleep is a step toward feeling better.",

"feeling stressed":"Stress can be tough, but you're stronger than you think 💪. Let's focus on improving your sleep little by little.",

"i cant handle this":"I'm really glad you shared this with me 💙. You're not alone, and things can improve with time and support.",

}
CONCERN_DATASET = {

"not good":"I'm really sorry your sleep hasn't been good lately 😔. Don't worry, many people go through this. We can slowly improve your sleep habits together. Try relaxing before bed and reducing screen time.",

"bad sleep":"That sounds tough 😟. Poor sleep can affect your energy and mood. But the good news is that small changes like a calm bedtime routine can help.",

"nightmares":"Nightmares can be scary 😔. They are often caused by stress or anxiety. Try relaxing before sleep and avoid scary content at night. You're safe and your mind will calm down.",

"i have nightmares":"I'm really sorry you're experiencing nightmares 😔. Try keeping your mind relaxed before sleep and practicing deep breathing. Nightmares usually reduce when stress is managed.",

"cant sleep":"That must be frustrating 😟. Try taking slow deep breaths and relaxing your mind. Your body will eventually feel sleepy.",

"cant sleep early":"It's okay, many people struggle with sleeping early 😊. Try reducing phone usage at night and gradually shifting your bedtime earlier.",

"unable to sleep":"I understand how difficult that can feel 😔. Try listening to calm music or reading something relaxing before bed.",

"sleep not regular":"Irregular sleep can happen due to busy schedules or stress. Try sleeping and waking at the same time every day.",

"sleep problem":"I'm really glad you told me about it 💙. Sleep problems are very common. Together we can find small ways to improve your sleep.",

"sleep was bad":"I'm sorry your sleep wasn't good 😞. Tonight you can try relaxing activities before bed like deep breathing or meditation.",

"tired":"Feeling tired all day can be exhausting 😔. Improving sleep quality slowly will help you regain energy.",

"very tired":"I'm sorry you're feeling so tired 😞. Your body may need more rest and relaxation.",

"sleepy":"Feeling sleepy during the day may mean your sleep quality needs improvement. Let's work on that together.",

"overthinking":"Overthinking at night happens to many people 😟. Try writing your thoughts in a notebook before bed.",

"thinking too much":"Your mind seems very active at night 😔. Try meditation or calm breathing before sleep.",

"stress":"Stress can definitely disturb sleep 😟. Relaxing activities like journaling or meditation may help.",

"too much stress":"I'm sorry you're feeling stressed 😔. Try taking slow breaths and relaxing your mind before sleep.",

"anxiety":"Anxiety at night can feel overwhelming. Remember that you're not alone and things can improve.",

"night anxiety":"Night anxiety happens to many people 😟. Try calming music or breathing exercises.",

"wake up at night":"Waking up at night can happen due to stress or sleep habits. Try keeping your room dark and calm.",

"wake up 3am":"Waking at 3 AM happens to many people. It may be due to stress or sleep cycle changes.",

"late sleep":"Sleeping late sometimes happens due to routine changes. Try slowly adjusting bedtime earlier.",

"sleep late":"That's okay 😊. Try reducing phone usage before bed to help your brain relax.",

"phone before sleep":"Phones emit blue light which reduces sleep hormones. Try avoiding them 30 minutes before sleep.",

"cant relax":"Relaxation before bed is important. Try deep breathing or listening to calm sounds.",

"feeling low":"I'm really sorry you're feeling low 😔. Getting good sleep can slowly improve mood.",

"i feel bad":"I'm really glad you shared that with me 💙. You're not alone and things can get better.",

"nothing works":"It may feel that way sometimes 😞 but small changes in sleep habits can slowly improve things.",

"help me":"Of course 😊 I'm here for you. Tell me more about your sleep problem.",

"need help":"I'm here to support you. Tell me what's troubling your sleep.",

"sleep advice":"Sure! Try keeping your room dark, avoiding caffeine at night, and relaxing before bed.",

"sleep tips":"Here are some simple tips: maintain a regular sleep schedule, avoid screens before bed, and keep your room quiet.",

"how improve sleep":"Improving sleep takes small steps. Try sleeping at the same time daily and relaxing before bed.",

"improve sleep":"That's a great goal! Small improvements like reading before bed can help.",

"good sleep":"That's wonderful! Maintaining good habits will keep your sleep healthy.",

"slept well":"That's great to hear! 😊 Keep maintaining those healthy sleep habits.",

"ok":"Alright 😊 Tell me more about your sleep habits.",

"yes":"That's great! I'm here to help you improve your sleep.",

"sure":"Awesome! Let's work together to improve your sleep.",

"hmm":"Take your time 😊 I'm here to listen.",

"bro cant sleep":"That sounds really frustrating 😔. Try calming your mind with breathing exercises.",

"not sleeping":"I'm sorry you're experiencing that 😞. Relaxing before bed may help.",

"sleep disturbed":"Disturbed sleep can happen due to stress or irregular routines.",

"sleep cycle bad":"Don't worry 😊 Sleep cycles can improve with small routine changes.",

"sleep quality bad":"Improving sleep environment and routine can help your sleep quality.",
"ideas to improve sleep":
"Of course bro 😊 Here are some simple things you can try tonight:\n"
"• Try sleeping at the same time every day\n"
"• Avoid phone usage 30 minutes before bed\n"
"• Keep your room dark and quiet\n"
"• Take slow deep breaths to relax\n"
"These small habits can really improve sleep over time 🌙",

"improve my sleep":
"I’m glad you want to improve your sleep 😊. Try these habits:\n"
"• Maintain a regular sleep schedule\n"
"• Avoid caffeine at night\n"
"• Reduce screen time before bed\n"
"• Do light stretching or meditation\n"
"Your body will slowly adjust to better sleep.",

"sleep ideas":
"Sure 😊 Here are some helpful sleep ideas:\n"
"• Read a book before bed instead of using your phone\n"
"• Keep your room cool and dark\n"
"• Drink warm milk or herbal tea\n"
"• Try relaxing breathing exercises.",

"sleep tips":
"Here are some simple sleep tips 🌙:\n"
"• Sleep and wake at the same time daily\n"
"• Avoid heavy meals late at night\n"
"• Keep your bedroom quiet and comfortable\n"
"• Relax your mind before bed.",

"sleep advice":
"I’d be happy to help 😊. To improve sleep you can:\n"
"• Create a calm bedtime routine\n"
"• Avoid bright screens before sleep\n"
"• Practice deep breathing\n"
"• Maintain consistent sleep timing.",

"help me improve sleep":
"Of course bro, let's improve your sleep together 😊:\n"
"• Try relaxing music before bed\n"
"• Avoid caffeine after evening\n"
"• Keep your bedroom dark\n"
"• Go to bed at the same time every night.",

"how improve sleep":
"Improving sleep takes small steps 🌙:\n"
"• Maintain a regular sleep schedule\n"
"• Avoid phone usage before bed\n"
"• Relax your mind with breathing exercises\n"
"• Keep your room calm and comfortable."
}

# ================= ROUTES =================== #

@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET","POST"])
def signup():

    if request.method == "POST":

        name=request.form["name"]
        dob=request.form["dob"]
        gender=request.form["gender"]
        username=request.form["username"]
        password=request.form["password"]

        age=datetime.now().year-int(dob.split("-")[0])

        user=User(name=name,dob=dob,age=age,gender=gender,
                  username=username,password=password)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":

        user=User.query.filter_by(
            username=request.form["username"],
            password=request.form["password"]
        ).first()

        if user:
            login_user(user)
            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():

    sleep_entries = SleepTrack.query.filter_by(
        user_id=current_user.id
    ).all()

    chart_labels = []
    chart_data = []
    for i, entry in enumerate(sleep_entries):
        chart_labels.append(f"Day {i+1}")
        chart_data.append(entry.score)

    return render_template(
        "dashboard.html",
        user=current_user,
        chart_labels=chart_labels,
        chart_data=chart_data
    )
@app.route("/track_sleep", methods=["POST"])
@login_required
def track_sleep():

    sleep_time = request.form["sleep_time"]
    wake_time = request.form["wake_time"]
    mood = request.form["mood"]

    score = 0

    # Sleep time scoring
    if sleep_time == "Before 10 PM":
        score += 3
    elif sleep_time == "10–11 PM":
        score += 2
    elif sleep_time == "11–12 AM":
        score += 1

    # Wake time scoring
    if wake_time == "6–7 AM":
        score += 3
    elif wake_time == "7–8 AM":
        score += 2
    elif wake_time == "Before 6 AM":
        score += 2

    # Mood scoring
    if mood == "Fresh":
        score += 3
    elif mood == "Normal":
        score += 2
    elif mood == "Tired":
        score += 1

    sleep_entry = SleepTrack(
        user_id=current_user.id,
        sleep_time=sleep_time,
        wake_time=wake_time,
        mood=mood,
        score=score,
        date=str(datetime.now().date())
    )

    db.session.add(sleep_entry)
    db.session.commit()

    return jsonify({"score": score})

# ================= CHAT =================== #
@app.route("/chat", methods=["POST"])
@login_required
def chat():

    user_message = request.json["message"].lower()

    # SPELL CORRECTION
    corrected = str(TextBlob(user_message).correct())

    # Combine original + corrected message
    message = user_message + " " + corrected


    # TAMIL / TANGLISH KEYWORDS
    tamil_map = {

# CANT SLEEP
"thoongala": "cant sleep",
"thoonga mudiyala": "cant sleep",
"thoongave mudiyala": "cant sleep",
"sleep varala": "cant sleep",
"thoongala bro": "cant sleep",
"thoongala da": "cant sleep",
"thoonga mudila": "cant sleep",

# NIGHTMARES
"kanavu": "nightmares",
"bayama kanavu": "nightmares",
"bayam kanavu": "nightmares",
"ketta kanavu": "nightmares",
"bayangara kanavu": "nightmares",
"bad kanavu": "nightmares",

# TIRED / SLEEPY
"romba tired": "very tired",
"romba tired ah iruken": "very tired",
"romba thoongu varuthu": "sleepy",
"thoongu varuthu": "sleepy",
"romba sleep varuthu": "sleepy",
"sleepy ah iruken": "sleepy",

# STRESS / OVERTHINKING
"romba yosikaren": "overthinking",
"yosikite iruken": "overthinking",
"mind calm illa": "stress",
"romba stress": "too much stress",
"tension ah iruku": "stress",
"romba tension": "too much stress",

# LATE SLEEP
"late ah thoonguren": "sleep late",
"late ah sleep panren": "sleep late",
"late sleep": "sleep late",
"night la late ah thoonguren": "sleep late",

# WAKE UP NIGHT
"night la elunthuduven": "wake up at night",
"night la elundhuruven": "wake up at night",
"3 mani ku elunthuduven": "wake up 3am",
"night la wake up aguthu": "wake up at night",

# SLEEP QUALITY
"sleep sari illa": "sleep not good",
"sleep correct ah illa": "sleep not good",
"sleep disturb aguthu": "sleep disturbed",
"sleep cycle sari illa": "sleep cycle bad",

# SLEEP IMPROVEMENT
"sleep improve panna": "improve sleep",
"sleep better aaganum": "improve sleep",
"sleep tips venum": "sleep tips",
"sleep advice venum": "sleep advice",
"epdi better sleep": "how improve sleep",

# GENERAL TALK
"seri": "ok",
"ok bro": "ok",
"nanri": "thank you",
"thanks bro" : "thank you",
"sleep song": "suggest tamil sleep song",
"song to sleep": "suggest tamil sleep song",
"tamil sleep song": "suggest tamil sleep song",
"song for sleep": "suggest tamil sleep song",
"lullaby": "suggest tamil sleep song",
"sleep music": "suggest tamil sleep song"
}

    for tamil_word, english_word in tamil_map.items():
        if tamil_word in message:
            message += " " + english_word
     # ================= TAMIL SLEEP SONGS PAGINATION ================= #
    song_keywords = ["sleep song", "tamil song", "tamil songs", 
                     "tamil songs sollu bro", "song to sleep", 
                     "give some tamil songs", "sleepy songs", "lullaby", "sleep music"]

    if any(keyword in user_message.lower() for keyword in song_keywords):
        if "song_index" not in session:
            session["song_index"] = 0

        start = session["song_index"]
        end = start + SONGS_PER_PAGE
        songs_to_send = TAMIL_SONG_LIST[start:end]

        song_message = "Here are some Tamil songs to help you sleep:\n\n"
        for song in songs_to_send:
            song_message += f"• {song}\n"

        session["song_index"] = end if end < len(TAMIL_SONG_LIST) else 0

        if end >= len(TAMIL_SONG_LIST):
            song_message += "\nThese are all the songs I have for now. We can start again from the beginning! 🌙"

        return jsonify({"reply": song_message})

    # CONCERN DATASET
    response = find_best_match(message, CONCERN_DATASET)
    if response:
        return jsonify({"reply": response})

    # EMPATHY DATASET
    response = find_best_match(message, EMPATHY_DATASET)
    if response:
        return jsonify({"reply": response})

    # SMALL TALK MATCH
    response = find_best_match(message, SMALL_TALK_DATASET)
    if response:
        return jsonify({"reply": response})
    # SLEEP DISORDER MATCH
    response = find_best_match(message, SLEEP_DISORDER_QA)
    if response:
        return jsonify({"reply": response})


    # ANONYMOUS QUESTIONS MATCH
    response = find_best_match(message, ANONYMOUS_QA)
    if response:
        return jsonify({"reply": response})

        # SLEEP DATASET MATCH
    response = find_best_match(message, SLEEP_DATASET)
    if response:
        return jsonify({"reply": response})
        

    # ================= DEFAULT RESPONSE ================= #
    return jsonify({
        "reply": "I understand you're having some sleep concerns 😔. Don't worry, I'm here to help you. Could you tell me a little more about what's happening with your sleep?"
    })

# ================= RUN ================= #

if __name__=="__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)