import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def hybrid_recommend(user_input, jobs_df):
    # Content-based filtering using TF-IDF
    # Combine relevant fields for better matching
    jobs_df['combined_text'] = jobs_df.apply(
        lambda x: f"{x['job_title']} {x['skills']} {x['description']} {x['location']}", 
        axis=1
    )
    
    # Create TF-IDF matrix
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(jobs_df['combined_text'])
    
    # Create user query
    user_query = ' '.join([
        user_input['job_title'],
        user_input['skills'],
        str(user_input['experience']),
        user_input['location']
    ])
    
    # Transform user query
    user_tfidf = vectorizer.transform([user_query])
    
    # Calculate similarity scores
    similarity_scores = cosine_similarity(user_tfidf, tfidf_matrix).flatten()
    
    # Get top 20 recommendations
    top_indices = np.argsort(similarity_scores)[-20:][::-1]
    recommendations = jobs_df.iloc[top_indices].to_dict('records')
    
    return recommendations 