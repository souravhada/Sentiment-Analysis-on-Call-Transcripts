from flask import Flask, request, jsonify
from transformers import pipeline
import os

app = Flask(__name__)
sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

def star_rating(sentiment_label):
    return int(sentiment_label.split()[0])  # Extract the star rating from the label

def analyze_transcript(content):
    results = []
    lines = content.splitlines()
    current_speaker = None
    current_text = ""

    sales_agent_ratings = []
    customer_ratings = []

    for line in lines:
        if line.strip():
            # Check if the line contains a timestamp and speaker
            if '[' in line and ']' in line:
                if current_speaker and current_text:  # Previous dialogue is complete
                    sentiment = sentiment_pipeline(current_text.strip())
                    star = star_rating(sentiment[0]['label'])
                    results.append({
                        'speaker': current_speaker,
                        'text': current_text.strip(),
                        'star_rating': star,
                        'score': sentiment[0]['score']
                    })

                    if 'Sales Agent' in current_speaker:
                        sales_agent_ratings.append(star)
                    elif 'Customer' in current_speaker:
                        customer_ratings.append(star)

                # Reset for new dialogue
                current_speaker = line.strip()
                current_text = ""
            else:
                # Continue accumulating text for the current dialogue
                current_text += line.strip() + " "

    # Handle the last dialogue in file
    if current_speaker and current_text:
        sentiment = sentiment_pipeline(current_text.strip())
        star = star_rating(sentiment[0]['label'])
        results.append({
            'speaker': current_speaker,
            'text': current_text.strip(),
            'star_rating': star,
            'score': sentiment[0]['score']
        })

        if 'Sales Agent' in current_speaker:
            sales_agent_ratings.append(star)
        elif 'Customer' in current_speaker:
            customer_ratings.append(star)

    avg_sales_agent_rating = sum(sales_agent_ratings) / len(sales_agent_ratings) if sales_agent_ratings else 0
    avg_customer_rating = sum(customer_ratings) / len(customer_ratings) if customer_ratings else 0
    overall_avg_rating = sum(sales_agent_ratings + customer_ratings) / len(sales_agent_ratings + customer_ratings) if (sales_agent_ratings + customer_ratings) else 0

    return results, avg_sales_agent_rating, avg_customer_rating, overall_avg_rating

@app.route('/analyze-file', methods=['POST'])
def analyze_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        content = file.read().decode('utf-8')
        results, avg_sales_agent_rating, avg_customer_rating, overall_avg_rating = analyze_transcript(content)

        return jsonify({
            'results': results,
            'avg_sales_agent_rating': avg_sales_agent_rating,
            'avg_customer_rating': avg_customer_rating,
            'overall_avg_rating': overall_avg_rating
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
