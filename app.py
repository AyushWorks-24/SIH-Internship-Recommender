# app.py (Final, Working Version with Enhanced UI)

import streamlit as st
import pandas as pd
from engine import RecommendationEngine
from admin_engine import AnalyticsEngine
import plotly.express as px
import plotly.graph_objects as go
import random
import time
from resume_parser import extract_skills_from_resume
import os

# --- Page Setup ---
st.set_page_config(
    page_title="AVSAR AI | Welcome",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ENHANCED Custom CSS ---
st.markdown("""
<style>
/* === 1. PROFESSIONAL BACKGROUND === */
[data-testid="stAppViewContainer"] > .main {
    background: linear-gradient(-45deg, #f0f8ff, #ffffff, #e6e9f0, #f8f9fa);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* === 2. GENERAL FONT & THEME === */
html, body, [class*="st-emotion-cache"] {
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #333;
}

/* === 3. ENHANCED SIDEBAR === */
[data-testid="stSidebar"] {
    background-color: #FDFDFD;
    border-right: 1px solid #e0e0e0;
}
[data-testid="stSidebar"] h2 {
    font-size: 1.8rem;
}
[data-testid="stSidebar"] .stButton>button {
    background-color: #f0f2f6;
    color: #333;
    border: 1px solid #d0d3d8;
    transition: all 0.2s ease-in-out;
}
[data-testid="stSidebar"] .stButton>button:hover {
    background-color: #e0e0e0;
    border-color: #007bff;
    color: #007bff;
}

/* === 4. MODERN TABS === */
[data-testid="stTabs"] button {
    background-color: #f0f2f6;
    border-radius: 8px;
    padding: 10px 16px;
    margin: 0 5px;
    border: 1px solid #d0d3d8;
    color: #555;
    transition: all 0.2s ease;
}
[data-testid="stTabs"] button:hover {
    background-color: #e0e0e0;
    color: #007bff;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    background-color: #007bff;
    color: white;
    border: 1px solid #0056b3;
}

/* === 5. CUSTOM INPUT FIELDS (TEXT, SELECTBOX, FILE UPLOADER) === */
[data-testid="stTextInput"] > div > div > input,
[data-testid="stSelectbox"] > div > div,
[data-testid="stFileUploader"] > div > div {
    background-color: #f8f9fa;
    border: 1px solid #d0d3d8;
    border-radius: 8px;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);
}
/* Focus effect for inputs */
[data-testid="stTextInput"]:focus-within > div > div > input,
[data-testid="stSelectbox"]:focus-within > div > div {
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
}

/* === 6. ENHANCED CARDS & CONTAINERS === */
.st-emotion-cache-183lzff { /* This targets st.container(border=True) */
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    border-radius: 12px;
    background-color: #ffffff;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); /* Slightly more pronounced base shadow */
    border: 1px solid #e0e0e0;
}
.st-emotion-cache-183lzff:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15); /* Stronger hover shadow */
}

/* === 7. BUTTON STYLING === */
.stButton>button {
    border-radius: 10px;
    font-weight: bold;
    padding: 0.75rem 1.5rem;
    transition: all 0.2s ease-in-out;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.stButton>button.primary {
    background-color: #007bff;
    color: white;
    border: none;
}
.stButton>button.primary:hover {
    background-color: #0056b3;
    color: white;
}

/* === 8. TYPOGRAPHY === */
h1 { color: #0056b3; font-size: 3.2rem; text-align: center; font-weight: 800; }
h2 { color: #007bff; font-size: 2.2rem; margin-top: 2.5rem; margin-bottom: 1.5rem; font-weight: 700; }
h3 { color: #007bff; font-size: 1.8rem; font-weight: 600; }
h4 { color: #333; font-size: 1.4rem; font-weight: 600; }
.tagline { font-size: 1.6rem; text-align: center; color: #555; margin-bottom: 2rem; font-weight: 300; }

/* === 9. ROLE SELECTION CARDS === */
.role-card {
    background-color: #ffffff;
    border-radius: 15px;
    padding: 30px;
    text-align: center;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    cursor: pointer;
    border: 2px solid transparent;
}
.role-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 25px rgba(0, 0, 0, 0.2);
    border-color: #007bff;
}
.role-icon { font-size: 4rem; margin-bottom: 15px; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2), -2px -2px 4px rgba(255, 255, 255, 0.8); display: inline-block; transition: transform 0.3s ease; }
.role-card:hover .role-icon { transform: scale(1.1); }
.role-student .role-icon { color: #28a745; }
.role-admin .role-icon { color: #007bff; }

/* === 10. LANDING PAGE SECTIONS === */
.how-it-works-section, .features-section {
    padding: 3rem 1rem;
    border-radius: 15px;
    margin: 3rem 0;
    background-color: rgba(255, 255, 255, 0.7); /* Make sections semi-transparent */
    backdrop-filter: blur(10px); /* Frosted glass effect */
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
}

</style>
""", unsafe_allow_html=True)


# --- Initialize Engines (Cached for performance) ---
# --- Optimized Data and Engine Loading ---

# Cache the data loading separately. This is very efficient.
@st.cache_data
def load_data():
    """Loads the CSV files into pandas DataFrames."""
    try:
        students_df = pd.read_csv('students.csv')
        internships_df = pd.read_csv('internships.csv')
        return students_df, internships_df
    except FileNotFoundError as e:
        st.error(f"Error loading data file: {e}")
        return None, None

# Cache the main recommendation engine resource.
@st.cache_resource
def load_recommendation_engine(students_df, internships_df):
    """Initializes the main recommendation engine."""
    return RecommendationEngine(students_df, internships_df)

# --- Main App Logic ---
students_df, internships_df = load_data()

if students_df is None or internships_df is None:
    st.error("Could not load necessary data. The app cannot continue.")
    st.stop()

# Load the main engine
engine = load_recommendation_engine(students_df, internships_df)

# IMPORTANT: We will now load the analytics_engine ONLY when the admin logs in.
# So, we remove it from the initial loading.

# --- Initialize Session State ---
if 'role' not in st.session_state:
    st.session_state.role = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'selected_internship_index' not in st.session_state:
    st.session_state.selected_internship_index = None
if 'student_profile_set' not in st.session_state:
    st.session_state.student_profile_set = False
if 'newly_added_students' not in st.session_state:
    st.session_state.newly_added_students = []
if 'applications' not in st.session_state:
    st.session_state.applications = []
if 'pro_access' not in st.session_state:
    st.session_state.pro_access = False
if 'skill_gap_result' not in st.session_state:
    st.session_state.skill_gap_result = None
if 'resume_suggestions' not in st.session_state:
    st.session_state.resume_suggestions = None
if 'application_log' not in st.session_state:
    st.session_state.application_log = []

api_key = st.secrets.get("GOOGLE_API_KEY")

# =================================================================================================
# --- VIEW 1: ROLE SELECTION LANDING PAGE ---
# =================================================================================================
if st.session_state.role is None:

    st.markdown("<h1>AVSAR AI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='tagline'>Don't Just Find an Internship. Build Your Career.</p>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3, col4 = st.columns([0.5, 2, 2, 0.5])

    with col2:
        st.markdown(
            f"""
            <div class="role-card role-student" onclick="document.getElementById('student_button').click()">
                <div class="role-icon">🎓</div>
                <h3>I am a Student</h3>
                <p>Unlock personalized internships & AI career tools.</p>
                <button id="student_button" style="display: none;">Student</button>
            </div>
            """, unsafe_allow_html=True
        )
        if st.button("Continue as Student", key="student_role_button", use_container_width=True, type="primary"):
            st.session_state.role = "Student"
            st.rerun()

    with col3:
        st.markdown(
            f"""
            <div class="role-card role-admin" onclick="document.getElementById('admin_button').click()">
                <div class="role-icon">💼</div>
                <h3>I am an Admin / Faculty</h3>
                <p>Access talent analytics & placement insights.</p>
                <button id="admin_button" style="display: none;">Admin</button>
            </div>
            """, unsafe_allow_html=True
        )
        if st.button("Continue as Admin", key="admin_role_button", use_container_width=True):
            st.session_state.role = "Admin"
            st.rerun()

    st.markdown("##")

    st.markdown("<div class='how-it-works-section'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>How AVSAR AI Works</h2>", unsafe_allow_html=True)
    hw_col1, hw_col2, hw_col3 = st.columns(3)
    with hw_col1:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center;'>1. Personalize Your Profile ✨</h4>", unsafe_allow_html=True)
            st.markdown(
                "<p style='text-align: center; padding: 0 1rem;'>Upload your resume and our AI instantly builds your skill profile.</p>",
                unsafe_allow_html=True)
    with hw_col2:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center;'>2. Get AI-Powered Matches 🎯</h4>", unsafe_allow_html=True)
            st.markdown(
                "<p style='text-align: center; padding: 0 1rem;'>Our smart engine finds the perfect, hyper-personalized internships for you.</p>",
                unsafe_allow_html=True)
    with hw_col3:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center;'>3. Achieve Your Career Goals 🚀</h4>", unsafe_allow_html=True)
            st.markdown(
                "<p style='text-align: center; padding: 0 1rem;'>Use our AI tools to analyze skill gaps, build the perfect resume, and track applications.</p>",
                unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='features-section'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Why Choose AVSAR AI?</h2>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center;'>🧠 Smart Recommendations</h4>", unsafe_allow_html=True)
            st.write("Our advanced AI ensures you see only the most relevant internships, saving you time and effort.")
    with f_col2:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center;'>📈 Data-Driven Insights</h4>", unsafe_allow_html=True)
            st.write("Understand the job market and your own potential with powerful analytics and skill gap reports.")
    with f_col3:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center;'>✨ AI-Powered Tools</h4>", unsafe_allow_html=True)
            st.write("From resume building to interview prep, get an edge with our integrated generative AI features.")
    st.markdown("</div>", unsafe_allow_html=True)


# =================================================================================================
# --- VIEW 2: STUDENT FLOW ---
# =================================================================================================
elif st.session_state.role == "Student":
    # --- Sidebar ---
    st.sidebar.title("AVSAR AI")
    st.sidebar.markdown("---")
    if st.sidebar.button("Go Back to Role Selection", use_container_width=True):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    st.sidebar.markdown("---")
    st.sidebar.toggle("Simulate AVSAR Pro Access", key="pro_access", help="Turn this on to preview the Pro Dashboard!")
    st.sidebar.markdown("---")
    with st.sidebar.expander("💡 About The Tech"):
        st.markdown("""
        - **Engine:** TF-IDF & Cosine Similarity.
        - **AI Helper:** Google's Generative AI.
        - **Analytics:** Pandas & Plotly.
        - **Resume Parser:** spaCy (NLP).
        """)
    st.sidebar.markdown("---")

    # --- Step 1 for Student: Select or Create Profile ---
    if not st.session_state.student_profile_set:
        st.title("First, let's set up your profile")
        _, mid_col, _ = st.columns([1, 2, 1])
        with mid_col:
            with st.container(border=True):
                profile_mode = st.radio("Choose Profile Type", ["👤 Existing Student", "✨ Create New Profile"],
                                        horizontal=True)
                if profile_mode == "👤 Existing Student":
                    student_names = engine.students_df['name'].tolist()
                    selected_student_name = st.selectbox("Select your profile:", options=student_names)
                    if st.button("Get Recommendations", use_container_width=True, type="primary"):
                        student_index = engine.students_df[engine.students_df['name'] == selected_student_name].index[0]
                        st.session_state.student_index = student_index
                        st.session_state.new_profile_data = None
                        st.session_state.selected_student_name = selected_student_name
                        st.session_state.student_profile_set = True
                        st.rerun()

                elif profile_mode == "✨ Create New Profile":
                    with st.form("new_student_form"):
                        st.markdown("#### Create Your Profile with AI")
                        name = st.text_input("Your Name *")
                        branch = st.text_input("Your Branch *")
                        location_preference = st.text_input("Preferred Location")
                        resume_file = st.file_uploader("Upload Your Resume (PDF or DOCX) *", type=["pdf", "docx"])
                        submitted = st.form_submit_button("Find Internships", use_container_width=True, type="primary")

                        if submitted:
                            if name and branch and resume_file:
                                if not os.path.exists("temp_resumes"):
                                    os.makedirs("temp_resumes")
                                file_path = os.path.join("temp_resumes", resume_file.name)
                                with open(file_path, "wb") as f:
                                    f.write(resume_file.getbuffer())

                                with st.spinner("🚀 Our AI is analyzing your resume..."):
                                    extracted_skills = extract_skills_from_resume(file_path)
                                    skills_str = ", ".join(extracted_skills)

                                if not extracted_skills:
                                    st.warning("Could not extract skills. Ensure your resume is text-based.")
                                    skills_str = ""
                                else:
                                    st.success(f"✅ Found {len(extracted_skills)} skills in your resume!")

                                new_profile = {
                                    "name": name, "branch": branch, "skills": skills_str,
                                    "location_preference": location_preference, "cgpa": 8.0
                                }
                                st.session_state.newly_added_students.append(new_profile)
                                st.session_state.student_index = None
                                st.session_state.new_profile_data = new_profile
                                st.session_state.selected_student_name = name
                                st.session_state.student_profile_set = True
                                st.rerun()
                            else:
                                st.error("Please fill in your name, branch, and upload your resume.")

    # --- Step 2 for Student: Show Dashboard after profile is set ---
    else:
        if st.session_state.pro_access:
            st.title(f"🚀 AVSAR Pro Dashboard for {st.session_state.selected_student_name}")
            st.markdown("---")
            st.subheader("📊 Placement Readiness Dashboard")
            with st.container(border=True):
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                m_col1.metric("Career Readiness Score", "85/100", "15 points to go!")
                m_col2.metric("Resume Score", "92%")
                m_col3.metric("Mock Interview Score", "78%")
                m_col4.metric("Skill Gaps Covered", "80%")
                st.progress(85)
            st.markdown("---")
            st.subheader("✨ Your Pro Tools")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                with st.container(border=True):
                    st.markdown("🎙️ **AI Interview Coach**")
                    st.write("Practice mock interviews with our AI and get instant feedback on your performance.")
                    st.button("Start Mock Interview", key="mock_interview", use_container_width=True)
                with st.container(border=True):
                    st.markdown("🔬 **Advanced Skill Gap Insights**")
                    st.write(
                        "Get a personalized learning plan with course links and time estimates to cover your skill gaps.")
                    st.button("View My Learning Plan", key="learning_plan", use_container_width=True)
                with st.container(border=True):
                    st.markdown("🏅 **Certificates & Badges**")
                    st.write("Showcase your skills by earning badges that you can display on your LinkedIn profile.")
                    st.button("View My Badges", key="badges", use_container_width=True)
            with p_col2:
                with st.container(border=True):
                    st.markdown("💬 **AI Career Chatbot**")
                    st.text_input("Ask me anything about your career...",
                                  placeholder="e.g., What skills do I need for a Product Manager role?")
                    st.button("Ask AI Coach", key="chatbot", use_container_width=True)
                with st.container(border=True):
                    st.markdown("📄 **AI Resume Builder**")
                    st.write(
                        "Automatically generate multiple, ATS-friendly resumes tailored for different job roles in one click.")
                    st.file_uploader("Upload your base resume to get started", type=['pdf', 'docx'])
                    st.button("Generate Tailored Resumes", key="resume_builder", use_container_width=True)
        else:
            if st.session_state.recommendations is None:
                if st.session_state.student_index is not None:
                    st.session_state.recommendations = engine.get_recommendations(st.session_state.student_index)
                else:
                    st.session_state.recommendations = engine.get_recommendations_for_new_profile(
                        st.session_state.new_profile_data)

            st.sidebar.header("🔍 Filters")
            all_states = ["All India"] + sorted(engine.internships_df['state'].unique().tolist())
            state_filter = st.sidebar.selectbox("State", options=all_states)
            city_filter = None
            if state_filter != "All India":
                cities_in_state = ["All Cities"] + sorted(
                    engine.internships_df[engine.internships_df['state'] == state_filter]['location'].unique().tolist())
                city_filter = st.sidebar.selectbox("City", options=cities_in_state)

            if st.sidebar.button("Apply Filters", use_container_width=True):
                with st.spinner("Updating..."):
                    if st.session_state.student_index is not None:
                        st.session_state.recommendations = engine.get_recommendations(st.session_state.student_index,
                                                                                      state_filter=state_filter,
                                                                                      city_filter=city_filter)
                    else:
                        st.session_state.recommendations = engine.get_recommendations_for_new_profile(
                            st.session_state.new_profile_data, state_filter=state_filter, city_filter=city_filter)
                    st.toast("Filters applied!", icon="✅")

            st.title(f"🎓 Dashboard for {st.session_state.selected_student_name}")
            rec_tab, app_tab, profile_tab = st.tabs(["🔍 Recommendations", "📝 My Applications", "👤 My Profile"])

            with rec_tab:
                recs = st.session_state.recommendations
                if recs.empty:
                    st.warning("No internships found matching your profile and filters.")
                else:
                    for index, row in recs.iterrows():
                        with st.container(border=True, key=f"rec_{index}"):
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                if 'company_logo_url' in row and pd.notna(row['company_logo_url']):
                                    st.image(row['company_logo_url'], width=100)
                                else:
                                    company_name = row['company']
                                    initials = "".join([name[0] for name in company_name.split()[:2]]).upper()
                                    st.markdown(f"""
                                    <div style="width:100px; height:100px; background-color:#f0f2f6; border-radius:10px; display:flex; justify-content:center; align-items:center;">
                                        <h2 style="color:#4f8bf9; font-family:sans-serif; margin:0;">{initials}</h2>
                                    </div>
                                    """, unsafe_allow_html=True)
                            with col2:
                                st.markdown(f"#### {row['domain']} at **{row['company']}**")
                                st.write(f"**📍 Location:** {row['location']}, {row['state']}")

                            st.write(f"**💰 Stipend:** ₹{row.get('stipend', 'N/A')} / month")
                            st.write(f"**🔧 Required Skills:** `{row['required_skills']}`")
                            st.markdown("---")

                            b_col1, b_col2 = st.columns(2)
                            with b_col1:
                                is_applied = any(app['internship_id'] == row['internship_id'] for app in
                                                 st.session_state.applications)
                                if st.button("Apply Now", key=f"apply_{index}", use_container_width=True,
                                             type="primary", disabled=is_applied):
                                    application_data = {'internship_id': row['internship_id'],
                                                        'Company': row['company'], 'Role': row['domain'],
                                                        'Status': random.choice(["Applied", "Under Review"])}
                                    st.session_state.applications.append(application_data)
                                    log_entry = {'Student Name': st.session_state.selected_student_name,
                                                 'Company': row['company'], 'Role': row['domain'],
                                                 'Applied At': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}
                                    st.session_state.application_log.append(log_entry)
                                    st.toast(f"✅ Applied for {row['domain']}!", icon="🎉")
                            with b_col2:
                                if st.button("Explore AI Tools", key=f"tools_{index}", use_container_width=True):
                                    if st.session_state.selected_internship_index == index:
                                        st.session_state.selected_internship_index = None
                                    else:
                                        st.session_state.selected_internship_index = index
                                    st.session_state.skill_gap_result = None
                                    st.session_state.resume_suggestions = None

                            if st.session_state.selected_internship_index == index:
                                st.markdown("---")
                                tool_col1, tool_col2 = st.columns(2)
                                with tool_col1:
                                    with st.container(border=True):
                                        st.markdown("<h6>Skill Gap Analysis</h6>", unsafe_allow_html=True)
                                        if st.button("Analyze Skill Gap", key=f"gap_{index}", use_container_width=True):
                                            with st.spinner("Analyzing..."):
                                                if st.session_state.student_index is not None:
                                                    st.session_state.skill_gap_result = engine.get_skill_gap_analysis(
                                                        st.session_state.student_index, index)
                                                else:
                                                    st.session_state.skill_gap_result = engine.get_skill_gap_for_new_profile(
                                                        st.session_state.new_profile_data, index)
                                        if st.session_state.skill_gap_result:
                                            res = st.session_state.skill_gap_result
                                            st.metric(label="Your Skill Match", value=f"{res['match_percentage']:.2f}%")
                                            st.progress(int(res['match_percentage']))
                                            if not res['missing_skills']:
                                                st.success("You have all required skills!")
                                            else:
                                                st.write("**❌ Missing Skills:**")
                                                for skill in res['missing_skills']:
                                                    st.markdown(
                                                        f"- {skill.replace('_', ' ').capitalize()} ([Learn]({res['learning_paths'].get(skill.capitalize(), '#')}))")
                                with tool_col2:
                                    with st.container(border=True):
                                        st.markdown("<h6>AI Resume Helper</h6>", unsafe_allow_html=True)
                                        if st.button("Generate Suggestions", key=f"resume_{index}",
                                                     use_container_width=True, disabled=(not api_key)):
                                            with st.spinner("Generating..."):
                                                if st.session_state.student_index is not None:
                                                    st.session_state.resume_suggestions = engine.get_resume_suggestions(
                                                        api_key, internship_index=index,
                                                        student_index=st.session_state.student_index)
                                                else:
                                                    st.session_state.resume_suggestions = engine.get_resume_suggestions(
                                                        api_key, internship_index=index,
                                                        new_profile_data=st.session_state.new_profile_data)
                                        if st.session_state.resume_suggestions:
                                            st.markdown(st.session_state.resume_suggestions)
                                        if not api_key: st.warning("Add Google AI API key to enable.")

            with app_tab:
                st.header("My Application Status")
                if not st.session_state.applications:
                    st.info("You haven't applied to any internships yet.")
                else:
                    apps_df = pd.DataFrame(st.session_state.applications)
                    st.dataframe(apps_df, use_container_width=True)

            with profile_tab:
                st.header("My Skill Profile")
                if st.session_state.student_index is not None:
                    student_info = engine.students_df.iloc[st.session_state.student_index].to_dict()
                else:
                    student_info = st.session_state.new_profile_data

                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    st.info(f"**Name:** {student_info.get('name', 'N/A')}")
                    st.info(f"**Branch:** {student_info.get('branch', 'N/A')}")
                with p_col2:
                    st.info(f"**CGPA:** {student_info.get('cgpa', 'N/A')}")
                    st.info(f"**Location Preference:** {student_info.get('location_preference', 'N/A')}")

                st.subheader("Skills Visualization")
                student_skills = [s.strip() for s in student_info.get('skills', '').split(',')]
                if student_skills and student_skills != ['']:
                    skill_levels = [random.randint(60, 95) for _ in student_skills]
                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatterpolar(r=skill_levels, theta=student_skills, fill='toself', name='Skill Proficiency',
                                        line=dict(color='deepskyblue')))
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False,
                                      title="Your Skill Radar")
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown("---")
                with st.expander("✏️ Update My Profile"):
                    with st.form("update_profile_form"):
                        st.write("Edit your details below and click save.")
                        updated_name = st.text_input("Name", value=student_info.get('name', ''))
                        updated_branch = st.text_input("Branch", value=student_info.get('branch', ''))
                        updated_skills = st.text_area("Skills (comma-separated)", value=student_info.get('skills', ''))
                        updated_location = st.text_input("Location Preference",
                                                         value=student_info.get('location_preference', ''))
                        submitted = st.form_submit_button("Save Changes")
                        if submitted:
                            updated_data = {
                                "name": updated_name, "branch": updated_branch, "skills": updated_skills,
                                "location_preference": updated_location, "cgpa": student_info.get('cgpa', 8.0)
                            }
                            if st.session_state.student_index is not None:
                                for key, value in updated_data.items():
                                    engine.students_df.loc[st.session_state.student_index, key] = value
                            else:
                                st.session_state.new_profile_data = updated_data
                            st.session_state.selected_student_name = updated_name
                            with st.spinner("Updating profile..."):
                                time.sleep(1)
                            st.success("Profile updated successfully!")
                            st.toast("Your profile has been saved!", icon="✅")


# =================================================================================================
# --- VIEW 3: ADMIN DASHBOARD ---
# =================================================================================================
elif st.session_state.role == "Admin":
    st.sidebar.title("AVSAR AI")
    st.sidebar.markdown("You are in **Admin View**")
    st.sidebar.markdown("---")
    if st.sidebar.button("Go Back to Role Selection", use_container_width=True):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    with st.sidebar.expander("💡 About The Tech"):
        st.markdown("""
        - **Engine:** TF-IDF & Cosine Similarity.
        - **AI Helper:** Google's Generative AI.
        - **Analytics:** Pandas & Plotly.
        """)
    st.header("💼 Talent Insights & Analytics")
    original_student_count = engine.students_df.shape[0]
    newly_added_count = len(st.session_state.newly_added_students)
    total_students = original_student_count + newly_added_count
    admin_m_col1, admin_m_col2, admin_m_col3, admin_m_col4 = st.columns(4)
    admin_m_col1.metric("Total Students", total_students)
    admin_m_col2.metric("Total Internships", engine.internships_df.shape[0])
    avg_stipend = pd.to_numeric(engine.internships_df['stipend'], errors='coerce').mean()
    admin_m_col3.metric("Avg. Monthly Stipend", f"₹{avg_stipend:,.0f}")
    top_skill = analytics_engine.get_skill_demand_supply_gap().iloc[0]['skill'].replace('_', ' ').capitalize()
    admin_m_col4.metric("Top Demanded Skill", top_skill)
    st.divider()
    admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs(
        ["📊 Market Overview", "🧑‍💻 Talent Search & Gaps", "🔥 Dynamic Talent Heatmap", "🔔 Live Application Feed"])

    with admin_tab1:
        st.subheader("Overview of the Internship Market")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Internships by Domain**")
            domain_counts = engine.internships_df['domain'].value_counts().head(10)
            fig_pie = px.pie(domain_counts, values=domain_counts.values, names=domain_counts.index,
                             title="Top 10 Internship Domains")
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.markdown("**Top Hiring Companies**")
            company_counts = engine.internships_df['company'].value_counts().head(10)
            fig_bar = px.bar(company_counts, x=company_counts.index, y=company_counts.values,
                             title="Top 10 Companies by Number of Internships",
                             labels={'x': 'Company', 'y': 'Number of Internships'})
            st.plotly_chart(fig_bar, use_container_width=True)

    with admin_tab2:
        colA, colB = st.columns(2)
        with colA:
            with st.container(border=True):
                st.subheader("Find Top Candidates")
                internship_titles = [f"{row['domain']} at {row['company']}" for idx, row in
                                     engine.internships_df.iterrows()]
                selected_internship_admin = st.selectbox("Select an internship:", options=internship_titles,
                                                         key="admin_internship_select")
                if st.button("Find Top Talent", use_container_width=True, type="primary"):
                    position = internship_titles.index(selected_internship_admin)
                    internship_index = engine.internships_df.index[position]
                    st.session_state.top_candidates = analytics_engine.find_top_candidates_for_internship(
                        internship_index)
                if 'top_candidates' in st.session_state and st.session_state.top_candidates is not None:
                    st.write("**Top Student Candidates:**")
                    st.dataframe(st.session_state.top_candidates[['name', 'branch', 'skills', 'match_score']],
                                 use_container_width=True)
        with colB:
            with st.container(border=True):
                st.subheader("National Skill Gap")
                if st.button("Generate Skill Gap Report", use_container_width=True, type="primary"):
                    with st.spinner("Analyzing skill gaps..."):
                        st.session_state.skill_gap_report = analytics_engine.get_skill_demand_supply_gap()
                if 'skill_gap_report' in st.session_state and st.session_state.skill_gap_report is not None:
                    st.write("**Top 10 Skill Gaps (High Demand, Low Supply):**")
                    st.dataframe(st.session_state.skill_gap_report[['skill', 'gap_score']].set_index('skill'),
                                 use_container_width=True)

    with admin_tab3:
        st.subheader("Dynamic Talent Heatmap by Location & Skills")
        all_skills_list = sorted(list(engine.skills_vocabulary))
        display_skills = [s.replace('_', ' ').capitalize() for s in all_skills_list]
        selected_display_skills = st.multiselect("Select skills to visualize:", options=display_skills,
                                                 default=["Python", "Machine learning", "React"])
        if st.button("Generate Talent Heatmap", use_container_width=True, type="primary"):
            if not selected_display_skills:
                st.warning("Please select at least one skill.")
            else:
                with st.spinner("Generating heatmap..."):
                    st.session_state.talent_heatmap = analytics_engine.get_talent_heatmap_data(selected_display_skills)
        if 'talent_heatmap' in st.session_state and st.session_state.talent_heatmap is not None and not st.session_state.talent_heatmap.empty:
            heatmap_df = st.session_state.talent_heatmap
            fig_heatmap = px.imshow(heatmap_df, labels=dict(x="Skill", y="Location", color="Number of Students"),
                                    text_auto=True, title="Concentration of Key Skills by Location",
                                    color_continuous_scale='Purples')
            st.plotly_chart(fig_heatmap, use_container_width=True)

    with admin_tab4:
        st.subheader("Live Application Feed")
        if not st.session_state.application_log:
            st.info("No students have applied for internships yet in this session.")
        else:
            log_df = pd.DataFrame(st.session_state.application_log)
            st.dataframe(log_df.sort_values(by="Applied At", ascending=False), use_container_width=True)

