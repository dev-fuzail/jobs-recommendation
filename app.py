from flask import Flask, request, jsonify, render_template
import pandas as pd
from recommender import hybrid_recommend
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json

app = Flask(__name__)

# Load job data
jobs_df = pd.read_csv('src/jobs.csv')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    user_input = {
        'job_title': data.get('job_title', ''),
        'skills': data.get('skills', ''),
        'experience': data.get('experience', ''),
        'location': data.get('location', '')
    }

    try:
        # Get system recommendations
        system_recommendations = hybrid_recommend(user_input, jobs_df)
        
        # Get AI recommendations from n8n
        try:
            print("Sending request to n8n...")
            n8n_response = requests.post(
                'http://localhost:5678/webhook/bbc18527-d0a3-4039-9e70-b36b4ae211d0',
                json={'message': f"Based on these criteria: {user_input}, recommend jobs"},
                headers={'Content-Type': 'application/json'}
            )
            
            ai_recommendation = None
            if n8n_response.ok:
                response_data = n8n_response.json()
                if isinstance(response_data, dict) and 'output' in response_data:
                    ai_recommendation = response_data['output']
                    print("Extracted AI Recommendation:", ai_recommendation)
                else:
                    ai_recommendation = "No AI recommendation available"
                    print("No valid recommendation found in response")
            else:
                print("N8N Error Response:", n8n_response.text)
                ai_recommendation = "Failed to get AI recommendation"
                
        except requests.exceptions.RequestException as e:
            print("N8N Request Error:", str(e))
            ai_recommendation = "Error connecting to AI service"
        
        return jsonify({
            'system_recommendations': system_recommendations,
            'ai_recommendation': ai_recommendation
        })
        
    except Exception as e:
        print('Detailed Error:', str(e))
        import traceback
        print('Traceback:', traceback.format_exc())
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 