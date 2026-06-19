import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import json
import os

# ================= 1. SYSTEM SETUP & SECURITY =================
st.set_page_config(page_title="AI Family Hub Ultra", page_icon="🏠", layout="wide")

# Fetch API key securely from Streamlit secrets
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if not API_KEY:
    st.error("⚠️ API Key missing! Please configure GEMINI_API_KEY in your Streamlit secrets.")
    st.stop()

# Configure the AI Model safely to prevent rate exceptions from blanking the dashboard
model = None
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    pass

# ================= 2. ULTRACLEAN HIGH-END DESIGN SYSTEM (CSS) =================
st.markdown("""
    <style>
        /* Base App Styling Overrides */
        .stApp {
            background-color: #080b10;
            color: #e2e8f0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #0f141c !important;
            border-right: 1px solid #1f293d !important;
        }
        
        /* Glassmorphism Card System */
        .custom-card {
            background: linear-gradient(145deg, #121824, #1a2336);
            padding: 24px;
            border-radius: 16px;
            border: 1px solid #26354a;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
            transition: all 0.3s ease;
        }
        .custom-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 8px 32px 0 rgba(59, 130, 246, 0.15);
        }
        
        /* Chore Status Cards */
        .chore-card-open {
            background: #161f30;
            border-left: 5px solid #6366f1;
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 15px;
            border-top: 1px solid #26354a;
            border-right: 1px solid #26354a;
            border-bottom: 1px solid #26354a;
        }
        .chore-card-claimed {
            background: #1a1e29;
            border-left: 5px solid #f59e0b;
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 15px;
            border-top: 1px solid #26354a;
            border-right: 1px solid #26354a;
            border-bottom: 1px solid #26354a;
        }
        .chore-card-done {
            background: #11221a;
            border-left: 5px solid #10b981;
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 15px;
            border-top: 1px solid #1b3a2b;
            border-right: 1px solid #1b3a2b;
            border-bottom: 1px solid #1b3a2b;
            opacity: 0.85;
        }
        
        /* Custom Section Specific Gradient Banners */
        .workspace-banner {
            background: linear-gradient(90deg, #1d4ed8, #7c3aed);
            padding: 20px;
            border-radius: 14px;
            margin-bottom: 25px;
            border: 1px solid #3b82f6;
            box-shadow: 0 4px 20px rgba(124, 58, 237, 0.2);
        }
        .workspace-banner h2 {
            color: #ffffff !important;
            margin: 0 !important;
            font-size: 26px;
        }
        .workspace-banner p {
            color: #cbd5e1 !important;
            margin: 5px 0 0 0 !important;
            font-size: 14px;
        }
        
        /* Premium Dashboard Metric Layouts */
        .metric-box {
            background: rgba(13, 17, 23, 0.6);
            border: 1px solid #22c55e;
            padding: 22px;
            border-radius: 14px;
            text-align: center;
            margin-bottom: 15px;
            box-shadow: 0 0 15px rgba(34, 197, 94, 0.1);
        }
        .metric-box-blue {
            background: rgba(13, 17, 23, 0.6);
            border: 1px solid #3b82f6;
            padding: 22px;
            border-radius: 14px;
            text-align: center;
            margin-bottom: 15px;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.1);
        }
        
        /* Appreciation Love Notes */
        .heart-wall-card {
            background: linear-gradient(135deg, #25122b, #3b1845);
            padding: 18px;
            border-radius: 14px;
            border: 1px solid #d946ef;
            margin-bottom: 15px;
            box-shadow: 0 4px 15px rgba(217, 70, 239, 0.15);
        }
        
        /* Typography Accents */
        h1, h2, h3, h4 {
            color: #3b82f6 !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }
        
        /* Pill Badges */
        .pill-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            background-color: #1e293b;
            color: #94a3b8;
            border: 1px solid #334155;
            margin-bottom: 10px;
        }
        .pill-badge-active {
            background-color: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border: 1px solid #3b82f6;
        }
        
        /* Custom Interactive Widgets Glow */
        .stTextArea textarea, .stTextInput input, .stNumberInput input {
            background-color: #090d16 !important;
            color: #f8fafc !important;
            border: 1px solid #26354a !important;
            border-radius: 10px !important;
            transition: all 0.25s ease;
        }
        .stTextArea textarea:focus, .stTextInput input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.3) !important;
        }
        .stButton>button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SYSTEM ROLE & PERSPECTIVE DATABASE =================
roles = ["Dad", "Mom", "Sister", "Brother"]

PERSPECTIVE_MAP = {
    "Dad": {"Mom": "Mom (Wife)", "Sister": "Daughter (Sister)", "Brother": "Son (Brother)"},
    "Mom": {"Dad": "Dad (Husband)", "Sister": "Daughter (Sister)", "Brother": "Son (Brother)"},
    "Sister": {"Dad": "Dad", "Mom": "Mom", "Brother": "Brother"},
    "Brother": {"Dad": "Dad", "Mom": "Mom", "Sister": "Sister"}
}

RELATIONSHIP_EXPLAINER = {
    "Dad": {"Mom": "Wife", "Sister": "Daughter", "Brother": "Son"},
    "Mom": {"Dad": "Husband", "Sister": "Daughter", "Brother": "Son"},
    "Sister": {"Dad": "Father", "Mom": "Mother", "Brother": "Brother"},
    "Brother": {"Dad": "Father", "Mom": "Mother", "Sister": "Sister"}
}

# ================= 4. RELIABLE GLOBAL STATE PERSISTENCE (JSON) =================
DATA_FILE = "family_hub_db.json"

def load_permanent_data():
    """Loads all logs and configurations permanently from a local JSON storage file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_permanent_data():
    """Serializes core structures to disk, ensuring data won't wipe out on reloads or switches."""
    data_to_save = {
        "user_passwords": st.session_state.user_passwords,
        "private_chat_history": st.session_state.private_chat_history,
        "family_inbox": st.session_state.family_inbox,
        "last_processed_vent": st.session_state.last_processed_vent,
        "hugs_count": st.session_state.hugs_count,
        "love_notes": st.session_state.love_notes,
        "household_needs": st.session_state.household_needs,
        "completed_chores": st.session_state.completed_chores,
        "health_budget": st.session_state.health_budget,
        "shared_calendar": st.session_state.shared_calendar,
        "user_rewards": st.session_state.user_rewards,
        "family_journal": st.session_state.family_journal
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data_to_save, f, indent=4)

# Execute baseline file read
saved_data = load_permanent_data()

# Inject permanent structures into active Session States
if "user_passwords" not in st.session_state:
    st.session_state.user_passwords = saved_data.get("user_passwords", {})

if "current_logged_in_user" not in st.session_state:
    st.session_state.current_logged_in_user = None

if "private_chat_history" not in st.session_state:
    st.session_state.private_chat_history = saved_data.get("private_chat_history", {r: [] for r in roles})

if "family_inbox" not in st.session_state:
    st.session_state.family_inbox = saved_data.get("family_inbox", {r: [] for r in roles})

if "last_processed_vent" not in st.session_state:
    st.session_state.last_processed_vent = saved_data.get("last_processed_vent", {r: None for r in roles})

if "hugs_count" not in st.session_state:
    st.session_state.hugs_count = saved_data.get("hugs_count", 0)

if "love_notes" not in st.session_state:
    st.session_state.love_notes = saved_data.get("love_notes", [])

if "household_needs" not in st.session_state:
    st.session_state.household_needs = saved_data.get("household_needs", [])

if "completed_chores" not in st.session_state:
    st.session_state.completed_chores = saved_data.get("completed_chores", [])

if "health_budget" not in st.session_state:
    st.session_state.health_budget = saved_data.get("health_budget", [])

if "shared_calendar" not in st.session_state:
    st.session_state.shared_calendar = saved_data.get("shared_calendar", [])

if "user_rewards" not in st.session_state:
    st.session_state.user_rewards = saved_data.get("user_rewards", {r: 0 for r in roles})

if "family_journal" not in st.session_state:
    st.session_state.family_journal = saved_data.get("family_journal", [])

# ================= 5. AI ENGINE UTILITIES WITH FIXED PERSPECTIVES =================
def ask_ai_assistant(user_role, message_text):
    if not model:
        return "⏳ **AI is offline.** Check your connection or API configuration settings."
    try:
        prompt = (
            f"You are a friendly, super supportive AI helper for a family member logged in as {user_role}. "
            f"Keep your tone relaxed, warm, and casual—like a close friend. Don't be formal or sound like an executive assistant. "
            f"Listen to their thought/vent, validate them, and offer simple, cozy advice.\n\nUser text: {message_text}"
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ AI Connection Issue: {str(e)}"

def translate_vent_for_family(sender_role, receiver_role, raw_vent_text):
    if not model:
        return raw_vent_text
    try:
        relationship = RELATIONSHIP_EXPLAINER.get(sender_role, {}).get(receiver_role, receiver_role)
        prompt = (
            f"You are a family mediator helper. You are helping a family member rewrite a raw thought into a nice, gentle message.\n"
            f"The sender is the '{sender_role}' and they are writing a message to their '{relationship}' (who is registered as '{receiver_role}').\n"
            f"Raw thought: \"\"\"{raw_vent_text}\"\"\"\n\n"
            f"TASK: Rewrite this into a calm, sweet, polite, and completely natural message addressed directly to the '{relationship}' (talking to them as 'you').\n\n"
            f"CRITICAL RULES:\n"
            f"1. Talk directly to them using 'you'. Do NOT reference their name or relationship in brackets.\n"
            f"2. NEVER use brackets, templates, or placeholders like '[Son's Name]', '[Name]', '[insert name]', or '[Receiver]'. Just use direct, natural wording.\n"
            f"3. Match the actual family connection. If a parent (Dad/Mom) is writing to their child (Son/Daughter), do NOT use sibling slang like 'Hey bro' or 'Hey sister'. Keep it warm, loving, and encouraging as a parent.\n"
            f"4. Keep it casual, warm, and cozy. Do not make it sound like a formal email or a business letter.\n\n"
            f"Output ONLY the clear, rewritten message body, with absolutely no placeholders."
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return raw_vent_text

def estimate_chore_difficulty(chore_text):
    if not model:
        return 2
    try:
        prompt = f"Rate the difficulty of this chore on a scale from 1 to 5 (1 = quick/easy, 5 = long/hard): '{chore_text}'. Return ONLY a single number."
        response = model.generate_content(prompt)
        return int(''.join(filter(str.isdigit, response.text.strip())) or 2)
    except:
        return 2

def verify_chore_photo_proof(chore_description, image_bytes):
    if not model:
        return "YES - Verification offline."
    try:
        img = Image.open(io.BytesIO(image_bytes))
        prompt = (
            f"You are evaluating a photo submitted by a family member to prove they finished a household chore.\n"
            f"Chore Name/Description: '{chore_description}'\n\n"
            f"Look closely at the image. Does it match and realistically show that this chore is completed or finished? "
            f"Answer with exactly 'YES' or 'NO' as the first word, followed by a very short, friendly 1-sentence explanation."
        )
        response = model.generate_content([prompt, img])
        return response.text.strip()
    except Exception as e:
        return "YES - Verification offline."

def analyze_vision_image(image_bytes, prompt_context):
    if not model:
        return "⏳ AI Vision system offline. Check API key."
    try:
        img = Image.open(io.BytesIO(image_bytes))
        response = model.generate_content([prompt_context, img])
        return response.text.strip()
    except Exception as e:
        return f"❌ Vision System Error: {str(e)}"

def generate_weekly_harmony_report():
    if not model:
        return "⏳ AI Engine offline. Cannot compile data reports."
    
    total_chores_left = len(st.session_state.household_needs)
    total_hugs = st.session_state.hugs_count
    total_expenses = sum(item["cost"] for item in st.session_state.health_budget)
    
    data_snapshot = f"""
    - Active Uncompleted Chores in Queue: {total_chores_left}
    - Total Emotional Support/Hugs Logged: {total_hugs}
    - Total Medical Pool Outflow: {total_expenses} AED
    - Appreciative Notes on Heart Wall: {len(st.session_state.love_notes)}
    """
    
    try:
        prompt = (
            "You are an expert family organizational analyst and harmony counselor. "
            "Analyze the following household data snapshot from the family app and write a brief, "
            "highly encouraging, witty, and motivating 'Weekly Family Performance Report'. "
            "Highlight their successes (like hugs or keeping bills tracked) and give them 1 friendly, "
            "actionable goal for next week based on their numbers. Keep it light, positive, and clear.\n\n"
            f"Household Data:\n{data_snapshot}"
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "📊 Free tier busy! Family logs are tracking beautifully on disk. Keep up the open communication!"

# ================= 6. SECURE LOGIN GATEWAY =================
if st.session_state.current_logged_in_user is None:
    st.markdown('<div class="custom-card" style="margin-top: 10%; max-width: 600px; margin-left: auto; margin-right: auto; text-align: center;">', unsafe_allow_html=True)
    st.markdown("<h1 style='color: #ffffff !important; font-size: 32px; margin-bottom: 5px;'>🏠 AI Family Hub</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 15px;'>Enter your secure communication gateway</p>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: left; margin-top: 25px;'>", unsafe_allow_html=True)
    login_user = st.selectbox("Select Family Profile Node:", roles, key="gatekeeper_user")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if login_user not in st.session_state.user_passwords:
        st.markdown('<div class="custom-card" style="max-width: 600px; margin-left: auto; margin-right: auto;">', unsafe_allow_html=True)
        st.markdown(f"<div class='pill-badge pill-badge-active'>🆕 New Profile Account: {login_user}</div>", unsafe_allow_html=True)
        with st.form("create_password_form"):
            new_pin = st.text_input("Create Secret PIN:", type="password")
            confirm_pin = st.text_input("Confirm PIN:", type="password")
            submit_setup = st.form_submit_button("🔒 Initialize Profile Access", use_container_width=True)
        if submit_setup and new_pin == confirm_pin and new_pin.strip():
            st.session_state.user_passwords[login_user] = new_pin
            st.session_state.current_logged_in_user = login_user
            save_permanent_data()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="custom-card" style="max-width: 600px; margin-left: auto; margin-right: auto;">', unsafe_allow_html=True)
        st.markdown(f"<div class='pill-badge'>🔐 Profile Authenticated PIN Required</div>", unsafe_allow_html=True)
        with st.form("login_form"):
            check_pass = st.text_input(f"Enter PIN for {login_user}:", type="password")
            submit_login = st.form_submit_button("🔓 Log In", use_container_width=True)
        if submit_login and check_pass == st.session_state.user_passwords[login_user]:
            st.session_state.current_logged_in_user = login_user
            st.rerun()
        elif submit_login:
            st.error("❌ Incorrect Profile Access Security PIN.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ================= 7. MAIN HUB ROUTING INTERFACE =================
selected_user = st.session_state.current_logged_in_user

st.sidebar.markdown(f"""
    <div style='background: linear-gradient(135deg, #1e293b, #0f172a); padding: 16px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px;'>
        <p style='margin: 0; color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase;'>Active User</p>
        <h3 style='margin: 4px 0; color: #ffffff !important; font-size: 20px;'>👤 {selected_user}</h3>
        <span style='background: rgba(34, 197, 94, 0.2); color: #4ade80; padding: 2px 8px; border-radius: 10px; font-size: 11px;'>⭐ {st.session_state.user_rewards[selected_user]} pts</span>
    </div>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 Terminate Session / Log Out", use_container_width=True):
    st.session_state.current_logged_in_user = None
    st.rerun()

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Workspaces Nodes", 
    [
        "🧠 Private AI Workspace", 
        "📬 Family Messages Feed", 
        "🤖 Invisible Household & Milestone Planner",
        "💖 Hugs & Love Tracker", 
        "🏠 Everyday Chores Board", 
        "📸 Memory & Activity Hub",
        "📊 Family Health Budget",
        "📊 Weekly Harmony Report"
    ]
)

# --- PANEL 1: PRIVATE AI BOT WORKSPACE ---
if menu == "🧠 Private AI Workspace":
    st.markdown("""
        <div class="workspace-banner">
            <h2>🧠 Private AI Workspace</h2>
            <p>Write out your raw thoughts. Talk to the AI helper, or safely rewrite them into sweet, polite notes for the family.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### 📝 Write What's On Your Mind")
    with st.form("vent_form", clear_on_submit=False):
        user_input = st.text_area("Your family won't see this raw text:", height=120, placeholder="Type freely here...")
        submit_vent = st.form_submit_button("Talk to AI Helper 🚀", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if submit_vent and user_input.strip():
        with st.spinner("Thinking..."):
            ai_response = ask_ai_assistant(selected_user, user_input)
            st.session_state.private_chat_history[selected_user].append((user_input, ai_response))
            st.session_state.last_processed_vent[selected_user] = user_input
            st.session_state[f"latest_ai_response_{selected_user}"] = ai_response
            save_permanent_data()

    if st.session_state.last_processed_vent[selected_user]:
        st.markdown('<h3>🤖 AI Advice</h3>', unsafe_allow_html=True)
        st.markdown('<div class="custom-card" style="border-left: 4px solid #3b82f6; background-color: #0b132b;">', unsafe_allow_html=True)
        st.write(st.session_state.get(f"latest_ai_response_{selected_user}", ""))
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("<h3>📤 Step 2: Clear up and Send a Note to Family</h3>", unsafe_allow_html=True)
        
        my_custom_perspectives = PERSPECTIVE_MAP[selected_user]
        
        col_select, col_actions = st.columns([2, 1])
        with col_select:
            selected_keys = st.multiselect(
                "Select Recipient Family Members:", 
                options=list(my_custom_perspectives.keys()),
                format_func=lambda x: my_custom_perspectives[x]
            )
        
        with col_actions:
            st.write("") 
            st.write("")
            generate_click = st.button("✨ Make Message Friendly", use_container_width=True)

        preview_key = f"preview_{selected_user}"
        
        if generate_click:
            if not selected_keys:
                st.warning("⚠️ Choose a family member to send it to first.")
            else:
                with st.spinner("Rewriting message..."):
                    primary_target_role = selected_keys[0]
                    clean_version = translate_vent_for_family(
                        selected_user, 
                        primary_target_role, 
                        st.session_state.last_processed_vent[selected_user]
                    )
                    st.session_state[preview_key] = {"msg": clean_version, "recipients": selected_keys}

        if preview_key in st.session_state and st.session_state[preview_key]:
            st.markdown("---")
            st.markdown("#### 📝 Preview of Message:")
            st.info(st.session_state[preview_key]["msg"])
            
            c1, c2 = st.columns(2)
            if c1.button("✅ Send to Inboxes", use_container_width=True):
                targets = st.session_state[preview_key]["recipients"]
                for target in targets:
                    st.session_state.family_inbox[target].append((selected_user, st.session_state[preview_key]["msg"]))
                
                save_permanent_data()
                st.success("📬 Message sent!")
                st.session_state[preview_key] = None
                st.session_state.last_processed_vent[selected_user] = None
                st.rerun()
                
            if c2.button("❌ Cancel Draft", use_container_width=True):
                st.session_state[preview_key] = None
                st.session_state.last_processed_vent[selected_user] = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 💬 History Log")
    if not st.session_state.private_chat_history[selected_user]:
        st.info("No records yet.")
    else:
        for msg, reply in reversed(st.session_state.private_chat_history[selected_user]):
            with st.chat_message("user"): 
                st.write(msg)
            with st.chat_message("assistant"): 
                st.write(reply)

# --- PANEL 2: FAMILY INBOX FEED ---
elif menu == "📬 Family Messages Feed":
    st.markdown("""
        <div class="workspace-banner" style="background: linear-gradient(90deg, #059669, #10b981);">
            <h2>📬 Family Messages Feed</h2>
            <p>Nice, friendly notes waiting for you from the family.</p>
        </div>
    """, unsafe_allow_html=True)
    
    inbox_messages = st.session_state.family_inbox[selected_user]
    if inbox_messages:
        for sender_role, clean_msg in reversed(inbox_messages):
            st.markdown('<div class="custom-card" style="border-left: 4px solid #10b981;">', unsafe_allow_html=True)
            sender_label = PERSPECTIVE_MAP[selected_user].get(sender_role, sender_role)
            st.markdown(f"<span class='pill-badge pill-badge-active'>From: {sender_label}</span>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 15px; color:#f1f5f9;'>{clean_msg}</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No new updates in your inbox right now.")

# --- PANEL 3: INVISIBLE HOUSEHOLD & MILESTONE PLANNER ---
elif menu == "🤖 Invisible Household & Milestone Planner":
    st.markdown("""
        <div class="workspace-banner" style="background: linear-gradient(90deg, #06b6d4, #0891b2);">
            <h2>🤖 Invisible Household & Milestone Planner</h2>
            <p>Streamline logistics, track milestones, scan newsletters, and map quick kitchen recipes with smart grocery loops.</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🗓️ Shared Timeline & Milestones", "📋 Document Parser & Morning Briefing", "🥦 Fridge Vision & Grocery Loops"])
    
    with tab1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("#### ➕ Add Calendar Event / Milestone")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            event_name = st.text_input("Event Name:")
            event_day = st.selectbox("Day:", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        with col_e2:
            event_notes = st.text_input("Quick Details/Notes:")
            
        if st.button("Add Event to Calendar", use_container_width=True) and event_name.strip():
            st.session_state.shared_calendar.append({
                "name": event_name,
                "day": event_day,
                "notes": event_notes,
                "logged_by": selected_user
            })
            save_permanent_data()
            st.success("Event saved!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.shared_calendar:
            st.markdown("### 🗓️ Upcoming Schedule & Milestones")
            for entry in st.session_state.shared_calendar:
                st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                c_m1, c_m2 = st.columns([4, 1])
                posted_by_label = PERSPECTIVE_MAP[selected_user].get(entry['logged_by'], "Me") if entry['logged_by'] != selected_user else "Me"
                c_m1.markdown(f"<span class='pill-badge pill-badge-active'>%s</span> <b style='font-size:16px; margin-left: 10px;'>%s</b>" % (entry['day'], entry['name']), unsafe_allow_html=True)
                c_m1.markdown(f"<p style='color: #94a3b8; margin: 5px 0 0 0;'>Info: {entry['notes']} | Added By: {posted_by_label}</p>", unsafe_allow_html=True)
                if c_m2.button("Delete", key=f"del_cal_{entry['name']}_{entry['day']}", use_container_width=True):
                    st.session_state.shared_calendar.remove(entry)
                    save_permanent_data()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
    with tab2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### 📷 Extract Calendar Events from Images")
        st.write("Take a picture of a school newsletter, camp schedule, or event email to instantly inject dates into the Shared Calendar.")
        
        newsletter_file = st.file_uploader("Upload Newsletter/Email Image:", type=["jpg", "jpeg", "png"], key="news_loader")
        if newsletter_file is not None:
            news_bytes = newsletter_file.read()
            st.image(news_bytes, caption="Uploaded Document Preview", width=250)
            
            if st.button("⚡ Extract Dates & Sync Calendar", use_container_width=True):
                with st.spinner("AI parsing text and identifying timeline events..."):
                    prompt = (
                        "Analyze this text or newsletter. Find all events, sports matches, school timelines, or bake sales. "
                        "Return a structured JSON list containing objects with keys: 'name', 'day', 'notes'. "
                        "The value for 'day' must map closely to standard weekday names (e.g., 'Monday', 'Tuesday') or specific descriptive times. "
                        "Provide ONLY valid JSON raw string array, with no markdown tags surrounding it."
                    )
                    ai_json_str = analyze_vision_image(news_bytes, prompt)
                    try:
                        extracted_events = json.loads(ai_json_str.strip("`").replace("json", ""))
                        for event in extracted_events:
                            st.session_state.shared_calendar.append({
                                "name": event.get("name", "Extracted Event"),
                                "day": event.get("day", "Monday"),
                                "notes": event.get("notes", ""),
                                "logged_by": f"AI Co-Pilot ({selected_user})"
                            })
                        save_permanent_data()
                        st.success(f"🎉 Successfully integrated {len(extracted_events)} schedule points into your Shared Calendar!")
                        st.rerun()
                    except Exception:
                        st.error("Could not auto-parse formatted milestones directly. Here is what the AI read:")
                        st.info(ai_json_str)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### ☀️ Request Morning Briefing Generator")
        if st.button("☕ Generate Today's Morning Briefing", use_container_width=True):
            with st.spinner("Syncing schedule database timelines..."):
                calendar_summary = json.dumps(st.session_state.shared_calendar)
                prompt = (
                    f"You are a warm, supportive, proactive home manager assistant giving a quick morning updates overview. "
                    f"Based on the following system calendar listings data: {calendar_summary}, draft a high-energy, helpful "
                    f"briefing. Remind the parent what events or schedules require attention. Keep it concise, casual, and conversational."
                )
                briefing_out = model.generate_content(prompt).text if model else "AI engine offline."
                st.info(briefing_out)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with tab3:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Fridge & Pantry Scan")
        st.write("Snap a photo of ingredients inside your kitchen, fridge or countertop to find simple recipes and build grocery list structures automatically.")
        
        fridge_file = st.file_uploader("Upload Area/Fridge Photo:", type=["jpg", "jpeg", "png"], key="fridge_loader")
        if fridge_file is not None:
            fridge_bytes = fridge_file.read()
            st.image(fridge_bytes, caption="Kitchen Environment Scan", width=250)
            
            if st.button("🍲 Generate Recipes & Missing Grocery Items List", use_container_width=True):
                with st.spinner("Analyzing ingredients inventory items..."):
                    prompt = (
                        "Look closely at these food items or storage area contents. "
                        "Provide 2 delicious, casual recipe concepts that can be constructed with these items. "
                        "Then, suggest a short, helpful grocery shopping list of missing ingredients or essentials that are typically paired with these dishes."
                    )
                    fridge_analysis = analyze_vision_image(fridge_bytes, prompt)
                    st.markdown("#### 📝 AI Kitchen Recommendation Assessment")
                    st.write(fridge_analysis)
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL 4: HUGS & LOVE TRACKER ---
elif menu == "💖 Hugs & Love Tracker":
    st.markdown("""
        <div class="workspace-banner" style="background: linear-gradient(90deg, #db2777, #ec4899);">
            <h2>💖 Appreciation & Heart Wall</h2>
            <p>Log physical family hugs or leave simple, sweet notes to make each other smile.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_h1, col_h2 = st.columns([2, 3])
    with col_h1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("#### Hug Tally")
        st.markdown(f"""
            <div class="metric-box" style="border-color: #ec4899;">
                <p style="color:#f3e8ff; margin:0; font-size:13px; font-weight:600;">Total Family Hugs Logged</p>
                <h1 style="color:#f472b6 !important; margin:8px 0 0 0; font-size:46px;">{st.session_state.hugs_count}</h1>
            </div>
        """, unsafe_allow_html=True)
        if st.button("We Just Hugged! 🤗", use_container_width=True):
            st.session_state.hugs_count += 1
            save_permanent_data()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("#### Hang a Heart Wall Note")
        note_txt = st.text_input("Type something sweet:")
        if st.button("Post it! ✨", use_container_width=True) and note_txt.strip():
            st.session_state.love_notes.append({"text": note_txt, "author": selected_user})
            save_permanent_data()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_h2:
        st.markdown("### 💌 The Family Heart Wall")
        if not st.session_state.love_notes:
            st.info("The wall is empty! Post something nice up there.")
        else:
            for idx, note in enumerate(reversed(st.session_state.love_notes)):
                true_note_idx = len(st.session_state.love_notes) - 1 - idx
                author_lbl = PERSPECTIVE_MAP[selected_user].get(note['author'], "Me") if note['author'] != selected_user else "Me"
                st.markdown(f"""
                    <div class="heart-wall-card">
                        <span style="color:#f472b6; font-size:16px;">💝 From {author_lbl}:</span>
                        <p style="color: #fdf2f8; font-size: 15px; margin: 6px 0 0 0; font-style: italic;">"{note['text']}"</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Take Down", key=f"del_note_{true_note_idx}", use_container_width=True):
                    st.session_state.love_notes.pop(true_note_idx)
                    save_permanent_data()
                    st.rerun()

# --- PANEL 5: EVERYDAY CHORES BOARD ---
elif menu == "🏠 Everyday Chores Board":
    st.markdown("""
        <div class="workspace-banner" style="background: linear-gradient(90deg, #6366f1, #4f46e5);">
            <h2>🏠 Family Chores Command Board</h2>
            <p>Add family responsibilities. Complete tasks by uploading a photo proof for AI verification to avoid cheating!</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### ➕ Post a New Household Chore")
    with st.form("add_chore_form", clear_on_submit=True):
        new_need_input = st.text_input("Chore Description:", placeholder="e.g., Wash the dishes or fold the clean laundry in the basket")
        submitted_chore = st.form_submit_button("Post to Chores Board 🚀", use_container_width=True)
        
    if submitted_chore and new_need_input.strip():
        with st.spinner("AI assessing chore workload..."):
            pts = estimate_chore_difficulty(new_need_input)
        st.session_state.household_needs.append({
            "need": new_need_input, 
            "posted_by": selected_user, 
            "claimed_by": "Unassigned",
            "points": pts
        })
        save_permanent_data()
        st.success("Chore added successfully!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    col_open, col_claimed, col_done = st.columns(3)

    with col_open:
        st.markdown("### 📋 Available Tasks")
        open_items = [item for item in st.session_state.household_needs if item['claimed_by'] == "Unassigned"]
        if not open_items:
            st.info("No open tasks left! Everything has been claimed.")
        else:
            for item in open_items:
                master_idx = st.session_state.household_needs.index(item)
                posted_label = PERSPECTIVE_MAP[selected_user].get(item['posted_by'], "Me") if item['posted_by'] != selected_user else "Me"
                
                st.markdown(f"""
                    <div class="chore-card-open">
                        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
                            <span style='background:#1e1e38; color:#818cf8; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:700; border:1px solid #312e81;'>⭐ {item.get('points', 2)} Pts</span>
                            <span style='color:#a5b4fc; font-size:11px;'>By: {posted_label}</span>
                        </div>
                        <p style='font-size:14px; margin:0 0 12px 0; color:#f8fafc; font-weight:500;'>{item['need']}</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Claim Task 🙋‍♂️", key=f"claim_card_{master_idx}", use_container_width=True):
                    st.session_state.household_needs[master_idx]['claimed_by'] = selected_user
                    save_permanent_data()
                    st.rerun()

    with col_claimed:
        st.markdown("### ⏳ In Progress")
        claimed_items = [item for item in st.session_state.household_needs if item['claimed_by'] != "Unassigned"]
        if not claimed_items:
            st.info("No chores are currently being worked on.")
        else:
            for item in claimed_items:
                master_idx = st.session_state.household_needs.index(item)
                posted_label = PERSPECTIVE_MAP[selected_user].get(item['posted_by'], "Me") if item['posted_by'] != selected_user else "Me"
                claimed_label = PERSPECTIVE_MAP[selected_user].get(item['claimed_by'], "Me") if item['claimed_by'] != selected_user else "Me"
                
                st.markdown(f"""
                    <div class="chore-card-claimed">
                        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
                            <span style='background:#2d1a0f; color:#fbbf24; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:700; border:1px solid #78350f;'>⏳ Active</span>
                            <span style='color:#fde68a; font-size:11px;'>Worker: {claimed_label}</span>
                        </div>
                        <p style='font-size:14px; margin:0 0 4px 0; color:#f8fafc; font-weight:500;'>{item['need']}</p>
                        <div style='font-size:11px; color:#94a3b8; margin-bottom:10px;'>Assigned By: {posted_label} | Value: {item.get('points', 2)} Pts</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if item['claimed_by'] == selected_user:
                    proof_file = st.file_uploader("📸 Upload completed photo proof:", type=["jpg", "png", "jpeg"], key=f"proof_{master_idx}")
                    if st.button("Submit Completion Proof ✅", key=f"verify_btn_{master_idx}", use_container_width=True):
                        if proof_file is None:
                            st.warning("⚠️ Lying detected! Please upload a photo showing that you actually finished the chore first.")
                        else:
                            proof_bytes = proof_file.read()
                            with st.spinner("AI checking photo proof..."):
                                verification_result = verify_chore_photo_proof(item['need'], proof_bytes)
                            
                            if verification_result.startswith("YES"):
                                earned = item.get('points', 2)
                                st.session_state.user_rewards[selected_user] += earned
                                archived_chore = st.session_state.household_needs.pop(master_idx)
                                archived_chore['completed_by'] = selected_user
                                st.session_state.completed_chores.append(archived_chore)
                                save_permanent_data()
                                st.success(f"🎉 Proof Approved! {verification_result[3:]}")
                                st.rerun()
                            else:
                                st.error(f"❌ Verification Failed! {verification_result[2:]}")

    with col_done:
        st.markdown("### 🎉 Recently Completed")
        if not st.session_state.completed_chores:
            st.info("No completed tasks logged yet.")
        else:
            for item in reversed(st.session_state.completed_chores[-5:]):
                completed_label = PERSPECTIVE_MAP[selected_user].get(item['completed_by'], "Me") if item['completed_by'] != selected_user else "Me"
                st.markdown(f"""
                    <div class="chore-card-done">
                        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                            <span style='background:#064e3b; color:#34d399; padding:2px 6px; border-radius:10px; font-size:10px; font-weight:700;'>✅ Verified</span>
                            <span style='color:#a7f3d0; font-size:11px;'>Earned By: {completed_label}</span>
                        </div>
                        <p style='font-size:13px; margin:0 0 4px 0; color:#cbd5e1; text-decoration: line-through;'>{item['need']}</p>
                        <span style='color:#34d399; font-size:11px; font-weight:600;'>+{item.get('points', 2)} Points Awarded</span>
                    </div>
                """, unsafe_allow_html=True)

# --- PANEL 6: FAMILY MEMORY & ACTIVITY HUB ---
elif menu == "📸 Memory & Activity Hub":
    st.markdown("""
        <div class="workspace-banner" style="background: linear-gradient(90deg, #ec4899, #f43f5e);">
            <h2>📸 Family Memory & Activity Hub</h2>
            <p>Plan unforgettable weekend outings and build a collaborative digital book of shared life highlights.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_mem1, col_mem2 = st.columns([2, 3])
    
    with col_mem1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### 🗺️ AI Outing Assistant")
        st.write("Stuck on what to do this weekend? Ask for custom ideas tailored to your location.")
        
        outing_prompt = st.text_area(
            "What kind of activity are you looking for?",
            value="We have a free Saturday in Abu Dhabi. What are some budget-friendly, kid-approved, outdoor activities within a 30-minute drive?",
            height=100
        )
        
        if st.button("🚀 Find Activities", use_container_width=True):
            with st.spinner("Searching and organizing top local opportunities..."):
                if model:
                    ai_ideas = model.generate_content(f"Provide excellent, specific family adventure activity options based on this request: {outing_prompt}").text
                    st.session_state["last_outing_suggestions"] = ai_ideas
                else:
                    st.session_state["last_outing_suggestions"] = "AI system is currently offline."
                    
        if "last_outing_suggestions" in st.session_state:
            st.markdown("#### 🌟 Suggested Outings Summary:")
            st.write(st.session_state["last_outing_suggestions"])
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_mem2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### 📖 Digital Family Memory Book Diary")
        st.write("Capture your family's favorite weekend highlight answers to build a lasting emotional anchor book.")
        
        with st.form("journal_entry_form", clear_on_submit=True):
            journal_text = st.text_area("What was the best thing your family did together this weekend?", placeholder="Type out a memory details snippet...")
            logged_by_who = st.selectbox("Who is capturing this thought?", roles)
            submit_journal = st.form_submit_button("💾 Save to Family Memory Book")
            
        if submit_journal and journal_text.strip():
            st.session_state.family_journal.append({
                "entry": journal_text,
                "author": logged_by_who
            })
            save_permanent_data()
            st.success("✨ Memory locked in permanently!")
            st.rerun()
            
        if st.session_state.family_journal:
            st.markdown("#### ⏳ Saved Family Highlights Logs")
            for record in reversed(st.session_state.family_journal):
                st.markdown(f"""
                    <div style='background: rgba(255,255,255,0.03); padding:14px; border-radius:10px; border:1px solid #334155; margin-bottom:10px;'>
                        <span class='pill-badge pill-badge-active'>Captured by {record['author']}</span>
                        <p style='margin:6px 0 0 0; font-style: italic; color:#f1f5f9;'>"{record['entry']}"</p>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL 7: ACCOUNTING & HEALTH BUDGET ---
elif menu == "📊 Family Health Budget":
    st.markdown("""
        <div class="workspace-banner" style="background: linear-gradient(90deg, #3b82f6, #2563eb);">
            <h2>📊 Health Budget Pool Ledger</h2>
            <p>Track shared family funds, pharmacy receipts, bills, and checkup costs together.</p>
        </div>
    """, unsafe_allow_html=True)
    
    b_col1, b_col2 = st.columns([1, 1])
    with b_col1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("#### Log a Medical Cost")
        item_title = st.text_input("Expense Description:", placeholder="e.g. Pharmacy Prescription Bill")
        item_cost = st.number_input("Transaction Amount (AED):", min_value=0.0, step=1.0)
        
        if st.button("Save Expense Entry", use_container_width=True) and item_title.strip():
            st.session_state.health_budget.append({
                "item": item_title,
                "cost": item_cost,
                "logged_by": selected_user
            })
            save_permanent_data()
            st.success("Saved to log pool!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("#### 📷 Instant Receipt Scanner")
        receipt_file = st.file_uploader("Upload a photo of a store receipt:", type=["jpg", "jpeg", "png"], key="receipt_loader")
        
        if receipt_file is not None:
            receipt_bytes = receipt_file.read()
            st.image(receipt_bytes, caption="Uploaded Document", width=150)
            if st.button("⚡ Scan Receipt Details", use_container_width=True):
                with st.spinner("Extracting total costs..."):
                    ai_extracted_receipt = analyze_vision_image(
                        receipt_bytes, 
                        "Read this receipt. Extract only the store/item name and the final grand total value. Format it simply as: Store/Item: [Name] | Cost: [Number only]."
                    )
                    st.session_state.health_budget.append({
                        "item": f"📷 Scan: {ai_extracted_receipt}",
                        "cost": 0.0, 
                        "logged_by": selected_user
                    })
                    save_permanent_data()
                    st.success("Receipt details logged successfully!")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
            
    with b_col2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("#### Financial Metrics Overview")
        total_spent = sum(item["cost"] for item in st.session_state.health_budget)
        
        st.markdown(f"""
            <div class="metric-box-blue">
                <p style="color:#94a3b8; margin:0; font-size:13px; font-weight: 600;">Total Capital Expended Outflow</p>
                <h2 style="margin:6px 0 0 0; color:#60a5fa !important; font-size: 32px;">{total_spent:,.2f} AED</h2>
            </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.health_budget:
            st.info("Ledger history is completely clear.")
        else:
            for idx, entry in enumerate(reversed(st.session_state.health_budget)):
                true_idx = len(st.session_state.health_budget) - 1 - idx
                c_e1, c_e2, c_e3 = st.columns([3, 2, 1])
                
                logger_label = PERSPECTIVE_MAP[selected_user].get(entry['logged_by'], "Me") if entry['logged_by'] != selected_user else "Me"
                c_e1.write(f"🧾 **{entry['item']}**")
                c_e2.write(f"`{entry['cost']:,} AED` | User: {logger_label}")
                
                if c_e3.button("Delete", key=f"del_exp_{true_idx}", use_container_width=True):
                    st.session_state.health_budget.pop(true_idx)
                    save_permanent_data()
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL 8: WEEKLY HARMONY REPORT ---
elif menu == "📊 Weekly Harmony Report":
    st.title("📊 Automated Weekly Family Report")
    st.caption("AI-generated insight report summarizing household logistics, emotional health, and budget tracking.")
    st.markdown("---")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
            <div class="metric-box">
                <p style="color:#58a6ff; margin:0; font-size:15px; font-weight:bold;">📋 Active Backlog Tasks</p>
                <h2 style="margin:5px 0 0 0; color:#fff;">{len(st.session_state.household_needs)} Chores</h2>
            </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
            <div class="metric-box">
                <p style="color:#ff6b81; margin:0; font-size:15px; font-weight:bold;">💖 Connection Points</p>
                <h2 style="margin:5px 0 0 0; color:#fff;">{st.session_state.hugs_count} Hugs Logged</h2>
            </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
            <div class="metric-box">
                <p style="color:#34d399; margin:0; font-size:15px; font-weight:bold;">💳 Financial Outflow</p>
                <h2 style="margin:5px 0 0 0; color:#fff;">{sum(item["cost"] for item in st.session_state.health_budget):,.2f} AED</h2>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("### 🤖 Executive AI Performance Assessment")
    
    if st.button("🔄 Compile New Live Report", use_container_width=True):
        with st.spinner("Parsing data points across database nodes..."):
            report_text = generate_weekly_harmony_report()
            st.session_state["cached_weekly_report"] = report_text
            
    if "cached_weekly_report" in st.session_state:
        st.markdown('<div class="custom-card" style="border-left: 4px solid #34d399;">', unsafe_allow_html=True)
        st.write(st.session_state["cached_weekly_report"])
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Click the button above to synthesize your household data logs into a custom report.")