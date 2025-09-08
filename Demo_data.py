
import pandas as pd
from faker import Faker
import random


def create_demo_data(num_students=101, num_internships=41):
    """
    Generates a smaller, lightweight demo dataset for the hackathon prototype.
    """
    fake = Faker('en_IN')

    
    CITY_STATE_MAP = {
        'Bangalore': 'Karnataka', 'Pune': 'Maharashtra', 'Hyderabad': 'Telangana',
        'Delhi': 'Delhi', 'Mumbai': 'Maharashtra', 'Chennai': 'Tamil Nadu',
        'Noida': 'Uttar Pradesh', 'Gurgaon': 'Haryana'
    }
    locations = list(CITY_STATE_MAP.keys()) + ['Remote']
    durations = ["2 Months", "3 Months", "6 Months"]

    branches = ['Computer Science', 'IT', 'Electronics', 'Mechanical', 'Civil', 'Electrical', 'Chemical',
                'Biotechnology', 'Aerospace']
    skills_pool = [
        'Python', 'Machine Learning', 'Data Analysis', 'SQL', 'Scikit-learn', 'Web Development', 'React', 'Node.js',
        'JavaScript', 'MongoDB', 'C++', 'Microcontrollers', 'Embedded Systems', 'IoT', 'Java',
        'Cloud Computing', 'AWS', 'Azure', 'DevOps', 'CAD', 'SolidWorks', 'MATLAB', 'Ansys', 'AutoCAD'
    ]
    companies = [
        'Google', 'Microsoft', 'Amazon', 'Tata Motors', 'Intel', 'Larsen & Toubro', 'NVIDIA', 'Flipkart',
        'Reliance Jio', 'Zomato', 'Siemens', 'Salesforce'
    ]
    domains = [
        'AI Research', 'Software Development', 'Cloud Engineering', 'Mechanical Design', 'Chip Design',
        'Civil Engineering', 'Deep Learning', 'Data Science', 'Network Engineering', 'Backend Development'
    ]

   
    student_data = []
    for i in range(101, 101 + num_students):
        student_data.append({
            'student_id': i, 'name': fake.name(), 'branch': random.choice(branches),
            'cgpa': round(random.uniform(7.0, 10.0), 2), 'location_preference': random.choice(locations),
            'skills': ', '.join(random.sample(skills_pool, k=random.randint(4, 7)))
        })
    students_df = pd.DataFrame(student_data)
    students_df.to_csv('students.csv', index=False)
    print(f"✅ Successfully created students.csv with {len(students_df)} entries.")

    
    internship_data = []
    for i in range(5001, 5001 + num_internships):
        location = random.choice(locations)
        state = CITY_STATE_MAP.get(location, 'N/A')
        internship_data.append({
            'internship_id': i, 'company': random.choice(companies), 'domain': random.choice(domains),
            'location': location, 'state': state,
            'stipend': random.randint(15, 80) * 1000,
            'duration': random.choice(durations),
            'required_skills': ', '.join(random.sample(skills_pool, k=random.randint(3, 5)))
        })
    internships_df = pd.DataFrame(internship_data)
    internships_df.to_csv('internships.csv', index=False)
    print(f"✅ Successfully created internships.csv with {len(internships_df)} entries.")


if __name__ == "__main__":

    create_demo_data(num_students=101, num_internships=41)
