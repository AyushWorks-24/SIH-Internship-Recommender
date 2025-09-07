import pandas as pd
import logging
import json
from sklearn.metrics.pairwise import cosine_similarity


class AnalyticsEngine:
    def __init__(self, engine):
        """
        Initializes the analytics engine using data from the main RecommendationEngine.
        """
        self.students_df = engine.students_df
        self.internships_df = engine.internships_df
        self.student_vectors = engine.student_vectors
        self.internship_vectors = engine.internship_vectors
        logging.info("Analytics Engine initialized successfully.")

    def find_top_candidates_for_internship(self, internship_index, top_n=5):
        """Finds the top N most suitable student candidates for a given internship."""
        internship_vector = self.internship_vectors[internship_index]
        similarity_scores = cosine_similarity(internship_vector, self.student_vectors)
        sorted_indices = similarity_scores[0].argsort()[::-1]
        top_indices = sorted_indices[:top_n]
        top_candidates = self.students_df.iloc[top_indices].copy()
        top_candidates['match_score'] = similarity_scores[0][top_indices]
        return top_candidates

    def get_skill_demand_supply_gap(self):
        """Analyzes the dataset to find the gap between skill demand and supply."""
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
        """Analyzes the student dataset to create a talent heatmap."""
        key_skills = ['machine_learning', 'python', 'react', 'web_development', 'cloud_computing', 'aws']
        heatmap_data = self.students_df[['location_preference', 'normalized_skills']].copy()
        for skill in key_skills:
            heatmap_data[skill] = heatmap_data['normalized_skills'].apply(lambda x: 1 if skill in x else 0)
        return heatmap_data.groupby('location_preference')[key_skills].sum()