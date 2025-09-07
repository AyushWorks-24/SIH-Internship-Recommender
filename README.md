**🚀 AI-Powered Internship Recommendation Engine (SIH)**

This repository contains the core AI engine and a standalone Flask API for the SIH Internship Recommendation project. The engine provides personalized internship recommendations, skill gap analysis, and other analytics.

**✨ Key Features**

1.AI-Powered Recommendations: A lightweight TF-IDF model that matches students to internships.

2.Skill Gap Analysis: An intelligent feature to show students the skills they are missing for a specific role.

3.Admin Analytics: Endpoints to find top candidates for an internship and analyze the national skill gap.

4.AI Based resume Keywords generation

**🛠️ Technology Stack**

1.AI & Machine Learning: Python, Pandas, NumPy, Scikit-learn

2.Backend API: Flask

3.Database (for prototype): SQLite (via CSV files)

4.Generative AI: Google Gemini (for planned features)

**⚙️ Setup and Installation**

To run the backend API service locally, please follow these steps.

1. Clone the Repository:





2. Create and Activate a Virtual Environment:



3. Install Dependencies:



**▶️ Running the API Server**

To start the backend server, run the following command from the main project directory.

Bash

python api.py

The server will start and be available at http://127.0.0.1:5000. This is the base URL for all API calls.

**📖 API Endpoints Documentation**

The API provides the following endpoints for the frontend application to consume.

**Get Recommendations for a Student**

URL: /recommendations

Method: GET

Query Parameter: student_id (integer)

Example Request: http://127.0.0.1:5000/recommendations?student_id=101

Example Success Response (JSON):

JSON

[
  {
    "company": "Google",
    "domain": "AI Research",
    "internship_id": 5001,
    "match_score": 0.85,
    "required_skills": "Machine Learning, Python"
  }
]

**Get Skill Gap Analysis**

URL: /skill_gap

Method: GET

Query Parameters: student_id (integer), internship_id (integer)

Example Request: http://127.0.0.1:5000/skill_gap?student_id=101&internship_id=5001

Example Success Response (JSON):

JSON

{
  "match_percentage": 75.0,
  "missing_skills": ["PyTorch"],
  "learning_paths": {
      "Pytorch": "https://www.youtube.com/results?search_query=PyTorch+tutorial"
  }

**📄 Generate AI Resume Suggestions** 

  
URL: /resume_suggestions

Method: GET

Query Parameters:

student_id (integer)

internship_id (integer)

Required Header:

X-API-KEY (string) - Your Google AI API Key.

Example Request:

http://127.0.0.1:5000/resume_suggestions?student_id=101&internship_id=5001
(Note: This request must be sent with the X-API-KEY header)

Example Success Response (JSON):

JSON

{
    "suggestions": "- Leveraged Python and Scikit-learn to analyze datasets, aligning with the core requirements of the Data Science role.\n- Developed a recommendation engine using TF-IDF and Cosine Similarity to match user profiles with relevant items.\n- Collaborated in a team hackathon environment to build a full-stack application from concept to deployment."
}
}
    "internship_id": 5001,
    "match_score": 0.85,
    "required_skills": "Machine Learning, Python"
  }
]
