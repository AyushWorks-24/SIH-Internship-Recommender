# app.py (Final, Complete, and Corrected Version)

import streamlit as st
import pandas as pd
from engine import RecommendationEngine
from admin_engine import AnalyticsEngine
import plotly.express as px
import plotly.graph_objects as go
import random
import time

# --- Page Setup ---
st.set_page_config(
    page_title="AVSAR AI | Welcome",
    page_icon="🚀",  # <-- This line is the fix
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for animations and new styles ---
st.markdown("""
<style>
/* Base Styling & Fonts */
html, body, [class*="st-emotion-cache"] {
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #333;
}

/* Card hover effect */
.st-emotion-cache-183lzff { /* This targets st.container(border=True) */
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    border-radius: 12px;
    background-color: #ffffff; /* Ensure cards have a white background */
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); /* Subtle initial shadow */
    border: 1px solid #e0e0e0; /* Light border */
}
.st-emotion-cache-183lzff:hover {
    transform: translateY(-5px); /* Lift effect */
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15); /* More pronounced shadow */
}

/* Main button styling */
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

/* Primary button specific styling */
.stButton>button.primary { /* Note: Streamlit sets type="primary" as a class now */
    background-color: #4CAF50; /* A fresh green */
    color: white;
    border: none;
}
.stButton>button.primary:hover {
    background-color: #45a049;
    color: white;
}

/* Secondary button styling */
.stButton>button:not(.primary) {
    background-color: #f0f2f6; /* Light grey */
    color: #333;
    border: 1px solid #d0d3d8;
}
.stButton>button:not(.primary):hover {
    background-color: #e0e0e0;
    color: #333;
}

/* Section titles */
h1 {
    color: #0056b3; /* Darker blue for main title */
    font-size: 3.2rem;
    text-align: center;
    font-weight: 800;
    line-height: 1.2;
}
h2 {
    color: #007bff; /* Bright blue for sub-sections */
    font-size: 2.2rem;
    margin-top: 2.5rem;
    margin-bottom: 1.5rem;
    font-weight: 700;
}
h3 {
    color: #007bff;
    font-size: 1.8rem;
    font-weight: 600;
}
h4 {
    color: #333;
    font-size: 1.4rem;
    font-weight: 600;
}

/* Hero Tagline */
.tagline {
    font-size: 1.6rem;
    text-align: center;
    color: #555;
    margin-bottom: 2rem;
    font-weight: 300;
}

/* Custom 3D-like Icon Cards for Role Selection */
.role-card {
    background-color: #f8f9fa; /* Light background for the card */
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
    border-color: #007bff; /* Highlight border on hover */
}
.role-icon {
    font-size: 4rem; /* Larger icon size */
    margin-bottom: 15px;
    /* Basic 3D effect with text-shadow */
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2), 
                 -2px -2px 4px rgba(255, 255, 255, 0.8);
    display: inline-block; /* Required for transform */
    transition: transform 0.3s ease;
}
.role-card:hover .role-icon {
    transform: scale(1.1); /* Slight bounce on icon hover */
}
.role-student .role-icon { color: #28a745; } /* Green for student */
.role-admin .role-icon { color: #007bff; }  /* Blue for admin */

/* Custom Container Backgrounds */
.how-it-works-section {
    background-color: #f0f8ff; /* Light blue background */
    padding: 3rem 0;
    border-radius: 15px;
    margin-top: 3rem;
    margin-bottom: 3rem;
}
.features-section {
    background-color: #fff9e6; /* Light yellow background */
    padding: 3rem 0;
    border-radius: 15px;
    margin-top: 3rem;
    margin-bottom: 3rem;
}

/* Center text within columns for sections */
.st-emotion-cache-1wv9vxf.e1f1d6z32 { /* Targeting columns */
    text-align: center;
}
.st-emotion-cache-1wv9vxf.e1f1d6z32 h4 {
    text-align: center;
}
.st-emotion-cache-1wv9vxf.e1f1d6z32 p {
    text-align: center;
    font-size: 1.1rem;
    line-height: 1.6;
    color: #666;
}

</style>
""", unsafe_allow_html=True)


# --- Initialize Engines (Cached for performance) ---
@st.cache_resource
def load_engines():
    """Load and initialize the recommendation and analytics engines."""
    try:
        recommendation_engine = RecommendationEngine(student_filepath='students.csv',
                                                     internship_filepath='internships.csv')
        analytics_engine = AnalyticsEngine(recommendation_engine)
        return recommendation_engine, analytics_engine
    except FileNotFoundError:
        st.error("Dataset files (students.csv, internships.csv) not found.")
        return None, None


engine, analytics_engine = load_engines()

if not engine or not analytics_engine:
    st.stop()

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
# --- VIEW 1: ROLE SELECTION LANDING PAGE (INNOVATIVE & 3D) ---
# =================================================================================================
if st.session_state.role is None:

    # --- 1. Hero Section with 3D-like Icons ---
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
        # Streamlit button to trigger the state change
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
        # Streamlit button to trigger the state change
        if st.button("Continue as Admin", key="admin_role_button", use_container_width=True):
            st.session_state.role = "Admin"
            st.rerun()

    st.markdown("##")  # Adds some vertical space

    # --- 2. "How It Works" Section (with background color) ---
    st.markdown("<div class='how-it-works-section'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #007bff;'>How AVSAR AI Works</h2>", unsafe_allow_html=True)
    hw_col1, hw_col2, hw_col3 = st.columns(3)
    with hw_col1:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center;'>1. Personalize Your Profile ✨</h4>", unsafe_allow_html=True)
            st.markdown(
                "<p style='text-align: center;'>Tell us your skills and career goals, whether you're an existing student or creating a new profile.</p>",
                unsafe_allow_html=True)
    with hw_col2:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center;'>2. Get AI-Powered Matches 🎯</h4>", unsafe_allow_html=True)
            st.markdown(
                "<p style='text-align: center;'>Our smart engine analyzes thousands of openings to find the perfect, hyper-personalized internships for you.</p>",
                unsafe_allow_html=True)
    with hw_col3:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center;'>3. Achieve Your Career Goals 🚀</h4>", unsafe_allow_html=True)
            st.markdown(
                "<p style='text-align: center;'>Use our AI tools to analyze skill gaps, build the perfect resume, and track your applications.</p>",
                unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # End of how-it-works-section
    st.markdown("##")

    # --- 3. Features Highlight Section (with background color) ---
    st.markdown("<div class='features-section'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #ffa500;'>Why Choose AVSAR AI?</h2>", unsafe_allow_html=True)
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
    st.markdown("</div>", unsafe_allow_html=True)  # End of features-section


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
    with st.sidebar.expander("💡 How It Works?"):
        st.markdown("""
        **AVSAR AI** uses a sophisticated approach to connect you with the right opportunities.
        - **Recommendation Engine:** We use **TF-IDF** and **Cosine Similarity** to match your profile.
        - **AI Resume Helper:** Our tool is powered by **Google's Generative AI**.
        - **Data Analytics:** Insights are generated using **Pandas** and visualized with **Plotly**.
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
                else:
                    with st.form("new_student_form"):
                        name = st.text_input("Your Name")
                        branch = st.text_input("Your Branch")
                        skills = st.text_input("Your Skills (comma-separated)")
                        location_preference = st.text_input("Preferred Location")
                        submitted = st.form_submit_button("Find Internships", use_container_width=True, type="primary")
                        if submitted:
                            new_profile = {"name": name, "branch": branch, "skills": skills,
                                           "location_preference": location_preference, "cgpa": 8.0}
                            st.session_state.newly_added_students.append(new_profile)
                            st.session_state.student_index = None
                            st.session_state.new_profile_data = new_profile
                            st.session_state.selected_student_name = name
                            st.session_state.student_profile_set = True
                            st.rerun()

    # --- Step 2 for Student: Show Dashboard after profile is set ---
    else:
        if st.session_state.pro_access:
            # --- AVSAR PRO DASHBOARD (RESTORED) ---
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
            # --- FREE DASHBOARD ---
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
                    st.warning("No internships found.")
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
                                if st.button("Explore Tools", key=f"tools_{index}", use_container_width=True):
                                    if st.session_state.selected_internship_index == index:
                                        st.session_state.selected_internship_index = None
                                    else:
                                        st.session_state.selected_internship_index = index
                                    st.session_state.skill_gap_result = None
                                    st.session_state.resume_suggestions = None
                            if st.session_state.selected_internship_index == index:
                                exp_col1, exp_col2 = st.columns(2)
                                with exp_col1:
                                    st.info("Skill Gap Analysis")
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
                                with exp_col2:
                                    st.info("AI Resume Helper")
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
                    for app in st.session_state.applications:
                        with st.container(border=True):
                            c1, c2 = st.columns([3, 1])
                            c1.markdown(f"#### {app['Role']}")
                            c1.markdown(f"**at {app['Company']}**")
                            status = app['Status']
                            if status == "Applied":
                                c2.info(f"**Status:** {status}")
                            elif status == "Under Review":
                                c2.warning(f"**Status:** {status}")
                            else:
                                c2.success(f"**Status:** {status}")
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
    with st.sidebar.expander("💡 How It Works?"):
        st.markdown("""
        - **Recommendation Engine:** Uses TF-IDF and Cosine Similarity.
        - **AI Resume Helper:** Powered by Google's Generative AI.
        - **Data Analytics:** Insights using Pandas and Plotly.
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
