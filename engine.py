import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import urllib.parse
import google.generativeai as genai
import logging
import json

class RecommendationEngine:
    def __init__(self, student_filepath, internship_filepath):
        self._setup_logging()
        logging.info("Initializing the AI Recommendation Engine...")
        self.students_df, self.internships_df = self._load_and_preprocess_data(student_filepath, internship_filepath)
        self._create_feature_vectors()
        logging.info("Engine initialized successfully.")

    def _setup_logging(self):
        for handler in logging.root.handlers[:]: logging.root.removeHandler(handler)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', filename='engine.log', filemode='a')

    def _normalize_skills(self, skills_string: str) -> str:
        if not isinstance(skills_string, str): return ''
        return ' '.join([skill.strip().replace(' ', '_') for skill in skills_string.lower().split(',')])

    def _load_and_preprocess_data(self, student_filepath, internship_filepath):
        students_df = pd.read_csv(student_filepath)
        internships_df = pd.read_csv(internship_filepath)
        text_cols_student = ['branch', 'skills', 'location_preference']
        text_cols_internship = ['domain', 'required_skills', 'location', 'state']
        for col in text_cols_student: students_df[col].fillna('', inplace=True)
        for col in text_cols_internship: internships_df[col].fillna('', inplace=True)
        students_df['normalized_skills'] = students_df['skills'].apply(self._normalize_skills)
        internships_df['normalized_skills'] = internships_df['required_skills'].apply(self._normalize_skills)
        students_df['profile_text'] = students_df['branch'].str.lower() + ' ' + students_df['location_preference'].str.lower() + ' ' + students_df['normalized_skills']
        internships_df['profile_text'] = internships_df['domain'].str.lower() + ' ' + internships_df['location'].str.lower() + ' ' + internships_df['state'].str.lower() + ' ' + internships_df['normalized_skills']
        return students_df, internships_df

    def _create_feature_vectors(self):
        all_profiles_text = pd.concat([self.students_df['profile_text'], self.internships_df['profile_text']], ignore_index=True)
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.vectorizer.fit(all_profiles_text)
        self.student_vectors = self.vectorizer.transform(self.students_df['profile_text'])
        self.internship_vectors = self.vectorizer.transform(self.internships_df['profile_text'])
        all_skills_text = pd.concat([self.students_df['normalized_skills'], self.internships_df['normalized_skills']], ignore_index=True)
        self.skill_vectorizer = TfidfVectorizer(stop_words='english')
        self.skill_vectorizer.fit(all_skills_text)
        self.student_skill_vectors = self.skill_vectorizer.transform(self.students_df['normalized_skills'])
        self.internship_skill_vectors = self.skill_vectorizer.transform(self.internships_df['normalized_skills'])
        self.skills_vocabulary = set(' '.join(all_skills_text).split())

    def get_recommendations(self, student_index, top_n=5, state_filter=None, city_filter=None):
        student_vector = self.student_vectors[student_index]
        similarity_scores = cosine_similarity(student_vector, self.internship_vectors)
        sorted_indices = similarity_scores[0].argsort()[::-1]
        recommended_internships = self.internships_df.iloc[sorted_indices].copy()
        recommended_internships['match_score'] = similarity_scores[0][sorted_indices]
        if state_filter and state_filter != 'All India':
            recommended_internships = recommended_internships[recommended_internships['state'] == state_filter]
        if city_filter and city_filter != 'All Cities':
            recommended_internships = recommended_internships[recommended_internships['location'] == city_filter]
        return recommended_internships.head(top_n)

    def get_recommendations_for_new_profile(self, new_profile_data, top_n=5, state_filter=None, city_filter=None):
        new_df = pd.DataFrame([new_profile_data])
        new_df['normalized_skills'] = new_df['skills'].apply(self._normalize_skills)
        new_df['profile_text'] = new_df['branch'].str.lower() + ' ' + new_df['location_preference'].str.lower() + ' ' + new_df['normalized_skills']
        new_student_vector = self.vectorizer.transform(new_df['profile_text'])
        similarity_scores = cosine_similarity(new_student_vector, self.internship_vectors)
        sorted_indices = similarity_scores[0].argsort()[::-1]
        recommended_internships = self.internships_df.iloc[sorted_indices].copy()
        recommended_internships['match_score'] = similarity_scores[0][sorted_indices]
        if state_filter and state_filter != 'All India':
            recommended_internships = recommended_internships[recommended_internships['state'] == state_filter]
        if city_filter and city_filter != 'All Cities':
            recommended_internships = recommended_internships[recommended_internships['location'] == city_filter]
        return recommended_internships.head(top_n)

    def add_new_student(self, new_profile_data):
        try:
            new_id = self.students_df['student_id'].max() + 1
            new_profile_data['student_id'] = new_id
            new_student_df = pd.DataFrame([new_profile_data])
            new_student_df['normalized_skills'] = new_student_df['skills'].apply(self._normalize_skills)
            new_student_df['profile_text'] = new_student_df['branch'].str.lower() + ' ' + new_student_df['location_preference'].str.lower() + ' ' + new_student_df['normalized_skills']
            self.students_df = pd.concat([self.students_df, new_student_df], ignore_index=True)
            self.students_df.to_csv('students.csv', index=False)
            self._create_feature_vectors()
            logging.info(f"Successfully added new student with ID: {new_id}")
            return new_id
        except Exception as e:
            logging.error(f"Failed to add new student. Error: {e}")
            return None

    def get_skill_gap_analysis(self, student_index, internship_index):
        student_vector = self.student_skill_vectors[student_index].toarray().flatten()
        internship_vector = self.internship_skill_vectors[internship_index].toarray().flatten()
        required_skill_indices = np.where(internship_vector > 0)[0]
        match_indices = np.where((internship_vector > 0) & (student_vector > 0))[0]
        gap_indices = np.where((internship_vector > 0) & (student_vector == 0))[0]
        if len(required_skill_indices) == 0: match_percentage = 100
        else: match_percentage = (len(match_indices) / len(required_skill_indices)) * 100
        all_skills = self.skill_vectorizer.get_feature_names_out()
        missing_skills = [all_skills[i] for i in gap_indices]
        matching_skills = [all_skills[i] for i in match_indices]
        learning_paths = {skill.replace('_', ' ').capitalize(): f"https://www.youtube.com/results?search_query={urllib.parse.quote(f'{skill.replace("_", " ")} tutorial')}" for skill in missing_skills}
        return {"match_percentage": match_percentage, "matching_skills": [s.replace('_', ' ') for s in matching_skills], "missing_skills": [s.replace('_', ' ') for s in missing_skills], "learning_paths": learning_paths}

    def get_skill_gap_for_new_profile(self, new_profile_data, internship_index):
        new_df = pd.DataFrame([new_profile_data])
        new_df['normalized_skills'] = new_df['skills'].apply(self._normalize_skills)
        student_vector = self.skill_vectorizer.transform(new_df['normalized_skills']).toarray().flatten()
        internship_vector = self.internship_skill_vectors[internship_index].toarray().flatten()
        required_skill_indices = np.where(internship_vector > 0)[0]
        match_indices = np.where((internship_vector > 0) & (student_vector > 0))[0]
        gap_indices = np.where((internship_vector > 0) & (student_vector == 0))[0]
        if len(required_skill_indices) == 0: match_percentage = 100
        else: match_percentage = (len(match_indices) / len(required_skill_indices)) * 100
        all_skills = self.skill_vectorizer.get_feature_names_out()
        missing_skills = [all_skills[i] for i in gap_indices]
        matching_skills = [all_skills[i] for i in match_indices]
        learning_paths = {skill.replace('_', ' ').capitalize(): f"https://www.youtube.com/results?search_query={urllib.parse.quote(f'{skill.replace("_", " ")} tutorial')}" for skill in missing_skills}
        return {"match_percentage": match_percentage, "matching_skills": [s.replace('_', ' ') for s in matching_skills], "missing_skills": [s.replace('_', ' ') for s in missing_skills], "learning_paths": learning_paths}

    def get_resume_suggestions(self, api_key, internship_index, student_index=None, new_profile_data=None):
        log_data = {"action": "get_resume_suggestions"}
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            if student_index is not None:
                student_skills = self.students_df.iloc[student_index]['skills']
                log_data["student_index"] = int(student_index)
            elif new_profile_data is not None:
                student_skills = new_profile_data['skills']
                log_data["student_name"] = new_profile_data['name']
            internship_skills = self.internships_df.iloc[internship_index]['required_skills']
            log_data["internship_index"] = int(internship_index)
            prompt = f'As a career coach, a student with skills: "{student_skills}" is applying for an internship needing: "{internship_skills}". Generate 3 concise, professional resume bullet points. Each must start with an action verb and highlight the student\'s relevant skills for this specific role. Do not invent skills.'
            response = model.generate_content(prompt)
            logging.info(json.dumps({**log_data, "success": True}))
            return response.text
        except Exception as e:
            logging.error(json.dumps({**log_data, "success": False, "error": str(e)}))
            return f"Could not generate resume suggestions: {e}"

    def find_top_candidates_for_internship(self, internship_index, top_n=5):
        internship_vector = self.internship_vectors[internship_index]
        similarity_scores = cosine_similarity(internship_vector, self.student_vectors)
        sorted_indices = similarity_scores[0].argsort()[::-1]
        top_indices = sorted_indices[:top_n]
        top_candidates = self.students_df.iloc[top_indices].copy()
        top_candidates['match_score'] = similarity_scores[0][top_indices]
        return top_candidates

    def get_skill_demand_supply_gap(self):
        internship_skills = self.internships_df['normalized_skills'].str.split().explode()
        skill_demand = internship_skills.value_counts().reset_index()
        skill_demand.columns = ['skill', 'demand_count']
        student_skills = self.students_df['normalized_skills'].str.split().explode()
        skill_supply = student_skills.value_counts().reset_index()
        skill_supply.columns = ['skill', 'supply_count']
        skill_gap_df = pd.merge(skill_demand, skill_supply, on='skill', how='outer').fillna(0)
        skill_gap_df['gap_score'] = skill_gap_df['demand_count'] - skill_gap_df['supply_count']
        return skill_gap_df.sort_values(by='gap_score', ascending=False).head(10)

    def get_talent_heatmap_data(self):
        key_skills = ['machine_learning', 'python', 'react', 'web_development', 'cloud_computing', 'aws']
        heatmap_data = self.students_df[['location_preference', 'normalized_skills']].copy()
        for skill in key_skills:
            heatmap_data[skill] = heatmap_data['normalized_skills'].apply(lambda x: 1 if skill in x else 0)
        return heatmap_data.groupby('location_preference')[key_skills].sum()