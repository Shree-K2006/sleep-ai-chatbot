const chatBox = document.getElementById("chatBox");

// Get user data
const userName = document.getElementById("userName")?.value || "User";
const userAge = parseInt(document.getElementById("userAge")?.value) || 19;

// Age-based problems
const AGE_PROBLEMS = {
    "13-18": [
        "Academic stress sleep disturbance",
        "Late night device usage",
        "Irregular sleep schedule",
        "Anxiety before exams"
    ],
    "19-35": [
        "Insomnia",
        "Overthinking at night",
        "Stress-related sleep disturbance",
        "Irregular sleep cycle"
    ],
    "36-55": [
        "Work stress insomnia",
        "Chronic insomnia",
        "Sleep apnea / snoring",
        "Fatigue / burnout"
    ],
    "56+": [
        "Light or fragmented sleep",
        "Early morning waking",
        "Restless legs syndrome",
        "Circadian rhythm issues"
    ]
};

let selectedProblem = "";

// Utility
function addMessage(text, className="bot-msg") {
    const msg = document.createElement("div");
    msg.className = className;
    msg.innerHTML = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addOptions(options, callback) {
    const div = document.createElement("div");
    div.style.marginTop = "10px";

    options.forEach(opt => {
        const btn = document.createElement("button");
        btn.innerText = opt;
        btn.style.margin = "5px";
        btn.style.padding = "8px 12px";
        btn.style.borderRadius = "8px";
        btn.style.border = "none";
        btn.style.backgroundColor = "#6c63ff";
        btn.style.color = "white";
        btn.style.cursor = "pointer";

        btn.onclick = () => {
            addMessage(opt, "user-msg");
            div.remove();
            callback(opt);
        };

        div.appendChild(btn);
    });

    chatBox.appendChild(div);
}

// Detect age group
function getAgeGroup(age) {
    if (age >= 13 && age <= 18) return "13-18";
    if (age >= 19 && age <= 35) return "19-35";
    if (age >= 36 && age <= 55) return "36-55";
    return "56+";
}

// Welcome user
function welcomeUser() {

    addMessage(`🤖 PeaceBot<br><br>
    Welcome <b>${userName}</b> 🌿<br><br>
    "A calm night creates a powerful tomorrow." 🌙<br><br>
    Based on your age (${userAge}), these sleep issues are commonly observed.<br>
    Which one are you experiencing?`);

    const group = getAgeGroup(userAge);
    addOptions(AGE_PROBLEMS[group], handleProblemSelection);
}

// Handle problem selection
function handleProblemSelection(problem) {

    selectedProblem = problem;

    addMessage(`Thank you for sharing that you are experiencing <b>${problem}</b>.<br><br>
    Have you taken any previous treatment for this problem?`);

    addOptions([
        "No previous treatment",
        "Yes, I took treatment but it did not work"
    ], handleTreatmentResponse);
}

// Treatment logic
function handleTreatmentResponse(choice) {

    if (choice === "No previous treatment") {
        giveBasicAdvice();
    } else {
        giveAdvancedAdvice();
    }
}

// BASIC ADVICE
function giveBasicAdvice() {

    addMessage(`
    Since you mentioned no previous treatment, starting with behavioral improvements is ideal.<br><br>

    🌙 <b>1. Fix Your Sleep Window</b><br>
    Sleep between 10:30 PM – 11:30 PM and wake at 6:30 – 7:00 AM daily.<br><br>

    📵 <b>2. Reduce Screen Exposure</b><br>
    Avoid screens 60 minutes before bed.<br><br>

    🧘 <b>3. Manage Overthinking</b><br>
    Practice 5–10 minutes of deep breathing or journaling.<br><br>

    ☕ <b>4. Avoid Late Caffeine</b><br>
    Do not consume caffeine after 4 PM.<br><br>

    🏃 <b>5. Light Evening Exercise</b><br>
    20–30 minutes walking improves sleep quality.<br><br>

    If symptoms continue beyond 3 weeks, consulting a sleep specialist is recommended.
    `);
}

// ADVANCED CASE
function giveAdvancedAdvice() {

    addMessage(`
    Thank you for telling me that. I appreciate that you've already tried treatment — that shows you are serious about improving your sleep. 🌿<br><br>

    Since it did not work, may I ask what kind of treatment it was?
    `);

    addOptions([
        "Medication prescribed by doctor",
        "Therapy / Counseling",
        "Home remedies",
        "Self-medication"
    ], finalAdvancedResponse);
}

// Final advanced structured response
function finalAdvancedResponse(type) {

    addMessage(`
    Thank you for sharing that it was <b>${type}</b>.<br><br>

    At age ${userAge}, ${selectedProblem} may be connected to:<br>
    • Anxiety<br>
    • Academic / Work stress<br>
    • Hormonal shifts<br>
    • Irregular circadian rhythm<br><br>

    🌙 <b>Step 1: 14-Day Sleep Reset</b><br>
    Fixed wake-up time daily<br>
    No daytime naps<br>
    15 minutes morning sunlight<br><br>

    🧠 <b>Step 2: Cognitive Wind-Down</b><br>
    10-minute journaling<br>
    5-minute 4-7-8 breathing<br><br>

    📵 <b>Step 3: Strict Digital Curfew</b><br>
    Stop screens 90 minutes before bed<br><br>

    🏃 <b>Step 4: Physical Regulation</b><br>
    Light evening exercise<br>
    Avoid caffeine after 2 PM<br><br>

    If previous treatment was ineffective, dosage reassessment or specialist evaluation may be required.<br><br>

    You are not failing — sleep disorders sometimes need approach adjustments. Improvement is absolutely possible. 🌙✨
    `);
}

// ================= CHAT SEND =================

function sendMessage(){

    const input=document.getElementById("userInput");
    const message=input.value.trim();

    if(message==="") return;

    addMessage(message,"user-msg");

    input.value="";

    fetch("/chat",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            message:message
        })
    })
    .then(res=>res.json())
    .then(data=>{
        addMessage(data.reply);
    })
    .catch(()=>{
        addMessage("⚠️ Response failed.");
    });
}

// ================= SLEEP TRACKER =================

document.getElementById("sleepForm")?.addEventListener("submit", function(e){

    e.preventDefault();

    const sleepTime = this.sleep_time.value;
    const wakeTime = this.wake_time.value;
    const mood = this.mood.value;

    let score = 0;

    if(sleepTime === "Before 10 PM") score += 30;
    else if(sleepTime === "10–11 PM") score += 25;
    else if(sleepTime === "11–12 AM") score += 15;
    else score += 5;

    if(wakeTime === "6–7 AM") score += 30;
    else if(wakeTime === "7–8 AM") score += 20;
    else score += 10;

    if(mood === "Fresh") score += 30;
    else if(mood === "Normal") score += 20;
    else if(mood === "Tired") score += 10;

    const box = document.getElementById("scoreBox");

    box.innerHTML = `
        <h3>🌙 Sleep Score</h3>
        <p>Your score: <b>${score}/90</b></p>
    `;
});

// Start
window.onload = welcomeUser;