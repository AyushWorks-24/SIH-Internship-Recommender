# api.py (Fully Featured Flask Version)

from flask import Flask, request, jsonify
import toml
import pandas as pd

# Import both of your engine classes
from engine import RecommendationEngine
from admin_engine import AnalyticsEngine

# --- 1. Initialize the Flask App and the AI Engines ---
print("Initializing Flask app and loading AI engines...")
app = Flask(__name__)

# Load the API key from secrets file
try:
    secrets = toml.load(".streamlit/secrets.toml")
    API_KEY = secrets.get("GOOGLE_API_KEY")
except Exception:
    API_KEY = None
    print("⚠️  Warning: .streamlit/secrets.toml not found. Resume suggestions will not work.")

# Load both engines once when the server starts
try:
    engine = RecommendationEngine(student_filepath='students.csv', internship_filepath='internships.csv')
    analytics_engine = AnalyticsEngine(engine)  # Initialize AnalyticsEngine with the main engine
    print("✅ Both engines loaded successfully.")
except Exception as e:
    print(f"❌ ERROR: Could not load engines. {e}")
    engine = None
    analytics_engine = None


# --- Helper Function to handle engine errors ---
def check_engine():
    if not engine or not analytics_engine:
        return {"error": "Engines not initialized on the server"}, 503
    return None, None


# --- 2. API Endpoints ---

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the AVSAR AI Flask API!"})


# --- Student Endpoints ---

@app.route('/student/recommendations', methods=['GET'])
def get_recommendations_api():
    error, status = check_engine()
    if error: return jsonify(error), status

    student_id = request.args.get('student_id', type=int)
    if student_id is None:
        return jsonify({"error": "Query parameter 'student_id' is required."}), 400
    try:
        student_index = engine.students_df[engine.students_df['student_id'] == student_id].index[0]
        recs = engine.get_recommendations(student_index)
        return jsonify(recs.to_dict('records'))
    except IndexError:
        return jsonify({"error": f"Student ID {student_id} not found."}), 404


@app.route('/student/recommendations/new_profile', methods=['POST'])
def get_new_profile_recommendations_api():
    error, status = check_engine()
    if error: return jsonify(error), status

    data = request.get_json()
    if not data or not all(key in data for key in ['branch', 'skills', 'location_preference']):
        return jsonify({"error": "Request body must contain 'branch', 'skills', and 'location_preference'."}), 400

    recs = engine.get_recommendations_for_new_profile(data)
    return jsonify(recs.to_dict('records'))


@app.route('/student/skill_gap', methods=['GET'])
def get_skill_gap_api():
    error, status = check_engine()
    if error: return jsonify(error), status

    student_id = request.args.get('student_id', type=int)
    internship_id = request.args.get('internship_id', type=int)
    if not all([student_id, internship_id]):
        return jsonify({"error": "Query parameters 'student_id' and 'internship_id' are required."}), 400
    try:
        student_index = engine.students_df[engine.students_df['student_id'] == student_id].index[0]
        internship_index = engine.internships_df[engine.internships_df['internship_id'] == internship_id].index[0]
        gap = engine.get_skill_gap_analysis(student_index, internship_index)
        return jsonify(gap)
    except IndexError:
        return jsonify({"error": "Student or Internship ID not found."}), 404


@app.route('/student/resume_suggestions', methods=['GET'])
def get_resume_suggestions_api():
    error, status = check_engine()
    if error: return jsonify(error), status
    if not API_KEY: return jsonify({"error": "API key not configured on the server."}), 500

    student_id = request.args.get('student_id', type=int)
    internship_id = request.args.get('internship_id', type=int)
    if not all([student_id, internship_id]):
        return jsonify({"error": "Query parameters 'student_id' and 'internship_id' are required."}), 400
    try:
        student_index = engine.students_df[engine.students_df['student_id'] == student_id].index[0]
        internship_index = engine.internships_df[engine.internships_df['internship_id'] == internship_id].index[0]
        suggestions = engine.get_resume_suggestions(API_KEY, student_index=student_index,
                                                    internship_index=internship_index)
        return jsonify({"suggestions": suggestions})
    except IndexError:
        return jsonify({"error": "Student or Internship ID not found."}), 404


# --- Admin Endpoints ---

@app.route('/admin/top_candidates', methods=['GET'])
def get_top_candidates_api():
    error, status = check_engine()
    if error: return jsonify(error), status

    internship_id = request.args.get('internship_id', type=int)
    if internship_id is None:
        return jsonify({"error": "Query parameter 'internship_id' is required."}), 400
    try:
        internship_index = \
        analytics_engine.internships_df[analytics_engine.internships_df['internship_id'] == internship_id].index[0]
        candidates = analytics_engine.find_top_candidates_for_internship(internship_index)
        return jsonify(candidates.to_dict('records'))
    except IndexError:
        return jsonify({"error": f"Internship ID {internship_id} not found."}), 404


@app.route('/admin/skill_gap_report', methods=['GET'])
def get_skill_gap_report_api():
    error, status = check_engine()
    if error: return jsonify(error), status

    report = analytics_engine.get_skill_demand_supply_gap()
    return jsonify(report.to_dict('records'))


@app.route('/admin/talent_heatmap', methods=['POST'])
def get_talent_heatmap_api():
    error, status = check_engine()
    if error: return jsonify(error), status

    data = request.get_json()
    if not data or 'skills' not in data or not isinstance(data['skills'], list):
        return jsonify({"error": "Request body must contain a 'skills' key with a list of strings."}), 400

    heatmap_data = analytics_engine.get_talent_heatmap_data(data['skills'])
    heatmap_data = heatmap_data.reset_index()  # Convert index to column for JSON
    return jsonify(heatmap_data.to_dict('records'))


# --- 3. Run the Flask App Server ---
if __name__ == '__main__':
    app.run(port=5000, debug=True)
