import streamlit as st
import requests
import json
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# Set page configuration
st.set_page_config(
    page_title="News Sentiment Analyzer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define API endpoint
API_URL = "http://localhost:8000"  # Change this to your FastAPI endpoint when deployed

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 0.5rem;
    }
    .sentiment-positive {
        color: #10B981;
        font-weight: 600;
    }
    .sentiment-negative {
        color: #EF4444;
        font-weight: 600;
    }
    .sentiment-neutral {
        color: #6B7280;
        font-weight: 600;
    }
    .topic-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        background-color: #E5E7EB;
        color: #4B5563;
        border-radius: 0.25rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.8rem;
    }
    .source-text {
        font-size: 0.8rem;
        color: #6B7280;
    }
    .loader {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_predefined_companies():
    """Get list of predefined companies from the API."""
    try:
        response = requests.get(f"{API_URL}/api/predefined-companies")
        return response.json().get("companies", [])
    except Exception as e:
        st.error(f"Error fetching predefined companies: {str(e)}")
        return ["Tesla", "Apple", "Microsoft", "Google", "Amazon"]  # Fallback

def analyze_company(company_name, num_articles=10):
    """Submit company for analysis to the API."""
    try:
        response = requests.post(
            f"{API_URL}/api/analyze",
            json={"company_name": company_name, "num_articles": num_articles}
        )
        return response.json()
    except Exception as e:
        st.error(f"Error submitting analysis request: {str(e)}")
        return {"status": "error", "message": str(e)}

def get_analysis_results(company_name):
    """Get analysis results from the API."""
    try:
        response = requests.get(f"{API_URL}/api/results/{company_name}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            st.error(f"Error: {response.json().get('detail')}")
            return None
    except Exception as e:
        st.error(f"Error fetching results: {str(e)}")
        return None

def display_sentiment_chart(data):
    """Display sentiment distribution chart."""
    sentiment_dist = data.get("comparative_analysis", {}).get("sentiment_distribution", {})
    
    if not sentiment_dist:
        st.warning("No sentiment data available for visualization")
        return
    
    fig = go.Figure()
    
    colors = {
        "Positive": "#10B981",  # Green
        "Negative": "#EF4444",  # Red
        "Neutral": "#6B7280"    # Gray
    }
    
    labels = list(sentiment_dist.keys())
    values = list(sentiment_dist.values())
    
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=[colors.get(label, "#E5E7EB") for label in labels]),
        textinfo="label+percent",
        insidetextorientation="radial"
    ))
    
    fig.update_layout(
        title="Sentiment Distribution",
        height=400,
        margin=dict(t=60, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_topics_chart(data):
    """Display common topics chart."""
    topics = data.get("comparative_analysis", {}).get("topic_analysis", {}).get("most_common_topics", [])
    
    if not topics:
        st.warning("No topic data available for visualization")
        return
    
    topic_names = [item.get("topic", "") for item in topics]
    topic_counts = [item.get("count", 0) for item in topics]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=topic_names,
        y=topic_counts,
        marker=dict(color="#3B82F6"),  # Blue
        text=topic_counts,
        textposition="auto"
    ))
    
    fig.update_layout(
        title="Most Common Topics",
        xaxis_title="Topic",
        yaxis_title="Count",
        height=400,
        margin=dict(t=60, b=50, l=20, r=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_article_card(article):
    """Display an article as a card."""
    st.markdown(f"""
    <div class="card">
        <div class="card-title">{article.get('title', 'Untitled')}</div>
        <p>{article.get('summary', 'No summary available')}</p>
        <div>
            Sentiment: <span class="sentiment-{article.get('sentiment', 'neutral').lower()}">{article.get('sentiment', 'Neutral')}</span>
        </div>
        <div style="margin-top: 0.5rem;">
            {"".join([f'<span class="topic-badge">{topic}</span>' for topic in article.get('topics', [])])}
        </div>
        <div class="source-text" style="margin-top: 0.5rem;">
            Source: {article.get('source', 'Unknown')} | Date: {article.get('date', 'Unknown')}
        </div>
        <div style="margin-top: 0.5rem;">
            <a href="{article.get('url', '#')}" target="_blank">Read full article</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main Streamlit application."""
    st.markdown('<h1 class="main-title">📰 News Sentiment Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Extract, analyze, and compare news sentiment for companies</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("Analysis Settings")
    
    # Get predefined companies
    predefined_companies = get_predefined_companies()
    
    # Company selection
    company_option = st.sidebar.selectbox(
        "Select a company",
        options=[""] + predefined_companies,
        index=0
    )
    
    custom_company = st.sidebar.text_input("Or enter a custom company name")
    
    # Determine company name
    company_name = custom_company if custom_company else company_option
    
    # Number of articles
    num_articles = st.sidebar.slider(
        "Number of articles to analyze",
        min_value=3,
        max_value=20,
        value=10,
        step=1
    )
    
    # Analysis button
    analyze_button = st.sidebar.button("Analyze News", type="primary")
    
    # Display info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("About")
    st.sidebar.info(
        "This application extracts news articles about a company, "
        "performs sentiment analysis, and generates insights. "
        "It also creates a Hindi audio summary of the findings."
    )
    
    # Main content
    if not company_name:
        st.info("👈 Select a company from the sidebar or enter a custom company name to begin analysis.")
        
        # Display sample results
        st.subheader("Example Analysis")
        st.markdown(
            "The analysis will generate insights similar to this example for Tesla:"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Sentiment Distribution:**
            - Positive: 60%
            - Negative: 20%
            - Neutral: 20%
            """)
            
        with col2:
            st.markdown("""
            **Common Topics:**
            - Electric Vehicles
            - Stock Market
            - Cybertruck
            - Self-Driving
            """)
        
        st.markdown("**Article Examples:**")
        st.markdown("""
        1. **Tesla's New Model Breaks Sales Records** (Positive)
           Summary: Tesla's latest EV sees record sales in Q3...
           
        2. **Regulatory Scrutiny on Tesla's Self-Driving Tech** (Negative)
           Summary: Regulators have raised concerns over Tesla's self-driving software...
        """)
        
        st.markdown("**Audio Summary:**")
        st.markdown("An audio summary in Hindi will be generated based on the analysis.")
        
    elif analyze_button:
        # Submit analysis request
        with st.status("Analyzing news for " + company_name, expanded=True) as status:
            st.write("Submitting analysis request...")
            result = analyze_company(company_name, num_articles)
            
            if result.get("status") == "processing":
                st.write("Request submitted successfully!")
                st.write("Waiting for analysis to complete...")
                
                # Set session state for auto-refresh
                if "company_being_analyzed" not in st.session_state:
                    st.session_state.company_being_analyzed = company_name
                
                # Add auto-refresh
                count = st_autorefresh(interval=3000, limit=20, key="analyze_refresh")
                
                # Check for results
                analysis_data = None
                for _ in range(10):  # Try a few times
                    analysis_data = get_analysis_results(company_name)
                    if analysis_data:
                        break
                    time.sleep(1)
                
                if analysis_data:
                    status.update(label="Analysis complete!", state="complete", expanded=False)
                    # Continue to display results
                else:
                    status.update(label=f"Analysis for {company_name} in progress...", state="running")
                    st.info("The analysis is still running. Please wait a moment and refresh the page.")
                    return
            else:
                status.update(label="Error in analysis", state="error")
                st.error(f"Error: {result.get('message', 'Unknown error')}")
                return
    
    # Display results if available
    analysis_data = get_analysis_results(company_name)
    
    if company_name and analysis_data:
        st.subheader(f"Sentiment Analysis for {analysis_data.get('company', company_name)}")
        
        # Display final sentiment
        st.markdown(f"""
        <div style="padding: 1rem; border-radius: 0.5rem; background-color: #EFF6FF; margin-bottom: 1.5rem;">
            <h3 style="margin-top: 0; color: #1E40AF;">Analysis Summary</h3>
            <p style="font-size: 1.1rem;">{analysis_data.get("final_sentiment", "No summary available")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display charts
        col1, col2 = st.columns(2)
        
        with col1:
            display_sentiment_chart(analysis_data)
            
        with col2:
            display_topics_chart(analysis_data)
        
        # Display audio
        st.subheader("Hindi Audio Summary")
        audio_url = analysis_data.get("audio_url")
        if audio_url:
            st.audio(f"{API_URL}{audio_url}")
        else:
            st.warning("Audio summary not available")
        
        # Display articles
        st.subheader("News Articles")
        
        articles = analysis_data.get("articles", [])
        if articles:
            # Create tabs for different sentiment categories
            all_tab, pos_tab, neg_tab, neu_tab = st.tabs([
                f"All Articles ({len(articles)})", 
                f"Positive ({sum(1 for a in articles if a.get('sentiment') == 'Positive')})",
                f"Negative ({sum(1 for a in articles if a.get('sentiment') == 'Negative')})",
                f"Neutral ({sum(1 for a in articles if a.get('sentiment') == 'Neutral')})"
            ])
            
            with all_tab:
                for article in articles:
                    display_article_card(article)
            
            with pos_tab:
                positive_articles = [a for a in articles if a.get('sentiment') == 'Positive']
                if positive_articles:
                    for article in positive_articles:
                        display_article_card(article)
                else:
                    st.info("No positive articles found")
            
            with neg_tab:
                negative_articles = [a for a in articles if a.get('sentiment') == 'Negative']
                if negative_articles:
                    for article in negative_articles:
                        display_article_card(article)
                else:
                    st.info("No negative articles found")
            
            with neu_tab:
                neutral_articles = [a for a in articles if a.get('sentiment') == 'Neutral']
                if neutral_articles:
                    for article in neutral_articles:
                        display_article_card(article)
                else:
                    st.info("No neutral articles found")
        else:
            st.warning("No articles available")
        
        # Display comparative analysis
        st.subheader("Comparative Analysis")
        
        coverage_differences = analysis_data.get("comparative_analysis", {}).get("coverage_differences", [])
        if coverage_differences:
            for i, diff in enumerate(coverage_differences):
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">Comparison {i+1}</div>
                    <p><strong>Observation:</strong> {diff.get('comparison', '')}</p>
                    <p><strong>Impact:</strong> {diff.get('impact', '')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No comparative analysis available")
        
        # Display topic overlap
        topic_overlap = analysis_data.get("comparative_analysis", {}).get("topic_analysis", {}).get("topic_overlap", {})
        if topic_overlap and topic_overlap.get("common_topics"):
            st.subheader("Topic Overlap Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Common Topics")
                common_topics = topic_overlap.get("common_topics", [])
                if common_topics:
                    for topic in common_topics:
                        st.markdown(f"- {topic}")
                else:
                    st.info("No common topics found")
            
            with col2:
                st.markdown("#### Unique Topics by Article")
                unique_topics = topic_overlap.get("unique_topics_by_article", {})
                if unique_topics:
                    for article, topics in unique_topics.items():
                        st.markdown(f"**{article}**")
                        for topic in topics:
                            st.markdown(f"- {topic}")
                else:
                    st.info("No unique topics found")

if __name__ == "__main__":
    main()