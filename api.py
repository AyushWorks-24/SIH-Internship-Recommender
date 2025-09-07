# api.py

from flask import Flask, request, jsonify
from engine import RecommendationEngine

# --- Initialize the Flask App and the AI Engine ---
print("Initializing Flask app and loading AI engine...")
app = Flask(__name__)

# Load the engine once when the server starts for best performance
try:
    engine = RecommendationEngine(student_filepath='students.csv', internship_filepath='internships.csv')
    print("✅ Engine loaded successfully.")
except Exception as e:
    print(f"❌ ERROR: Could not load engine. {e}")
    engine = None


# --- Define API Endpoints (The URLs) ---

@app.route('/')
def home():
    return "AI Recommendation Engine API is running."


@app.route('/recommendations', methods=['GET'])
def get_recommendations_api():
    if not engine:
        return jsonify({"error": "Engine not initialized"}), 500

    # Get student_id from the URL query (e.g., /recommendations?student_id=101)
    student_id = request.args.get('student_id', type=int)

    if student_id is None:
        return jsonify({"error": "Please provide a 'student_id' parameter."}), 400

    try:
        student_index = engine.students_df[engine.students_df['student_id'] == student_id].index[0]
    except IndexError:
        return jsonify({"error": f"Student with ID {student_id} not found."}), 404

    recommendations = engine.get_recommendations(student_index)

    # Convert the pandas DataFrame to a list of dictionaries (JSON)
    return jsonify(recommendations.to_dict('records'))


@app.route('/skill_gap', methods=['GET'])
def get_skill_gap_api():
    if not engine:
        return jsonify({"error": "Engine not initialized"}), 500

    student_id = request.args.get('student_id', type=int)
    internship_id = request.args.get('internship_id', type=int)

    if student_id is None or internship_id is None:
        return jsonify({"error": "Please provide both 'student_id' and 'internship_id' parameters."}), 400

    try:
        student_index = engine.students_df[engine.students_df['student_id'] == student_id].index[0]
        internship_index = engine.internships_df[engine.internships_df['internship_id'] == internship_id].index[0]
    except IndexError:
        return jsonify({"error": f"Student ID {student_id} or Internship ID {internship_id} not found."}), 404

    skill_gap_analysis = engine.get_skill_gap_analysis(student_index, internship_index)

    return jsonify(skill_gap_analysis)


# --- Run the Flask App Server ---
if __name__ == '__main__':
    app.run(port=5000, debug=True)