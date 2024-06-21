import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.title("Sentiment Analysis Application")

uploaded_file = st.file_uploader("Choose a transcript file", type="txt")

# Function to map star ratings to sentiment colors
def map_sentiment_color(star_rating):
    if star_rating == 5:
        return "#5cb85c"  # Green
    elif star_rating == 4:
        return "#9acd32"  # Light Green
    elif star_rating == 3:
        return "#ffffff"  # White
    elif star_rating == 2:
        return "#f0ad4e"  # Light Orange
    elif star_rating == 1:
        return "#d9534f"  # Red

if uploaded_file is not None:
    content = uploaded_file.read().decode('utf-8')
    st.text_area("File Content", content, height=300)

    if st.button("Analyze Sentiment"):
        files = {'file': uploaded_file.getvalue()}
        response = requests.post('http://localhost:5000/analyze-file', files=files)

        if response.status_code == 200:
            result = response.json()
            st.write("### Analysis Results")
            st.write("Displaying the sentiment analysis results:")

            # Convert results to DataFrame
            df = pd.DataFrame(result['results'])

            # Map star ratings to sentiment colors
            df['color'] = df['star_rating'].map(map_sentiment_color)

            st.dataframe(df[['speaker', 'text', 'star_rating', 'score']])

            # Calculate and display average ratings
            avg_sales_agent_rating = result['avg_sales_agent_rating']
            avg_customer_rating = result['avg_customer_rating']
            overall_avg_rating = result['overall_avg_rating']

            st.write(f"**Average Sales Agent Rating:** {avg_sales_agent_rating:.2f} stars")
            st.write(f"**Average Customer Rating:** {avg_customer_rating:.2f} stars")
            st.write(f"**Overall Average Rating:** {overall_avg_rating:.2f} stars")

            # Display the description for star ratings
            st.write("""
            ### Star Rating Descriptions
            - **5 Stars**: Positive
            - **4 Stars**: Slightly Positive
            - **3 Stars**: Neutral
            - **2 Stars**: Slightly Negative
            - **1 Star**: Negative
            """)

            # Visualize ratings with a bar chart
            st.write("### Rating Visualization")
            ratings = pd.DataFrame({
                'Role': ['Sales Agent', 'Customer', 'Overall'],
                'Average Rating': [avg_sales_agent_rating, avg_customer_rating, overall_avg_rating],
                'Color': ['#5cb85c', '#9acd32', '#f0ad4e']  # Colors for each rating
            })

            fig, ax = plt.subplots()
            bars = ax.bar(ratings['Role'], ratings['Average Rating'], color=ratings['Color'])
            ax.set_ylim(0, 5)
            ax.set_ylabel('Average Rating (Stars)')
            ax.set_title('Average Sentiment Ratings')

            # Add text labels above the bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.2f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')

            st.pyplot(fig)

            # Download option for results
            st.write("### Download Results")
            csv = df.to_csv(index=False)
            st.download_button(label="Download data as CSV", data=csv, file_name='sentiment_analysis_results.csv', mime='text/csv')

        else:
            st.write("Error: Could not get a response from the sentiment analysis API.")

# Add footer
st.markdown("""
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        color: grey;
    }
    </style>
    <div class="footer">
        <p>Made by Sourav Hada</p>
    </div>
""", unsafe_allow_html=True)
