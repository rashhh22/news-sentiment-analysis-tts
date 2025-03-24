from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os
import json
from models.news_extractor import NewsExtractor
from models.sentiment_model import SentimentAnalyzer
from models.comparative_analyzer import ComparativeAnalyzer
from models.tts_converter import TTSConverter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="News Sentiment Analysis API",
    description="API for extracting and analyzing news articles for companies",
    version="1.0.0"
)

# Initialize components
news_extractor = NewsExtractor()
sentiment_analyzer = SentimentAnalyzer()
comparative_analyzer = ComparativeAnalyzer()
tts_converter = TTSConverter()

# Cache for storing results
cache = {}

# Create directory for audio files if it doesn't exist
os.makedirs("audio_files", exist_ok=True)

# Pydantic models for request/response validation
class CompanyRequest(BaseModel):
    company_name: str
    num_articles: Optional[int] = 10

class ArticleResponse(BaseModel):
    title: str
    summary: str
    sentiment: str
    topics: List[str]
    url: str
    source: str
    date: str

class ComparativeResponse(BaseModel):
    sentiment_distribution: Dict[str, int]
    coverage_differences: List[Dict[str, str]]
    topic_analysis: Dict[str, Any]
    final_sentiment: str

class FullAnalysisResponse(BaseModel):
    company: str
    articles: List[Dict[str, Any]]
    comparative_analysis: Dict[str, Any]
    final_sentiment: str
    audio_url: str

# Background task for processing news
def process_news(company_name: str, num_articles: int):
    """Background task to process news for a company."""
    try:
        # Extract news articles
        articles = news_extractor.fetch_news(company_name, num_articles)
        
        # Analyze sentiment
        articles_with_sentiment = sentiment_analyzer.analyze_articles(articles)
        
        # Perform comparative analysis
        comparison = comparative_analyzer.analyze(articles_with_sentiment)
        
        # Generate report for TTS
        tts_report = f"News sentiment analysis for {company_name}. {comparison['final_sentiment']} "
        
        # Add details about sentiment distribution
        sentiments = comparison['sentiment_distribution']
        tts_report += f"Out of {sum(sentiments.values())} articles, "
        tts_report += f"{sentiments.get('Positive', 0)} were positive, "
        tts_report += f"{sentiments.get('Negative', 0)} were negative, and "
        tts_report += f"{sentiments.get('Neutral', 0)} were neutral. "
        
        # Add information about main topics
        if comparison['topic_analysis'].get('most_common_topics'):
            topics = [item['topic'] for item in comparison['topic_analysis']['most_common_topics'][:3]]
            if topics:
                tts_report += f"The most discussed topics were {', '.join(topics)}. "
        
        # Convert to speech
        audio_file = tts_converter.text_to_speech(
            tts_report, 
            output_path=f"audio_files/{company_name.replace(' ', '_')}_report.mp3"
        )
        
        # Prepare results
        formatted_articles = []
        for article in articles_with_sentiment:
            formatted_articles.append({
                "title": article.get('title', 'Untitled'),
                "summary": article.get('summary', ''),
                "sentiment": article.get('sentiment', {}).get('sentiment', 'Neutral'),
                "topics": article.get('topics', []),
                "url": article.get('url', ''),
                "source": article.get('source', 'Unknown'),
                "date": article.get('date', 'Unknown')
            })
        
        # Store in cache
        cache[company_name] = {
            "company": company_name,
            "articles": formatted_articles,
            "comparative_analysis": comparison,
            "final_sentiment": comparison['final_sentiment'],
            "audio_url": f"/audio/{company_name.replace(' ', '_')}_report.mp3"
        }
        
        logger.info(f"Finished processing news for {company_name}")
        
    except Exception as e:
        logger.error(f"Error in background processing for {company_name}: {str(e)}")
        # Store error in cache
        cache[company_name] = {"error": str(e)}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "News Sentiment Analysis API",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/api/companies", "method": "GET", "description": "Get list of pre-analyzed companies"},
            {"path": "/api/analyze", "method": "POST", "description": "Analyze news for a company"},
            {"path": "/api/results/{company_name}", "method": "GET", "description": "Get analysis results for a company"},
            {"path": "/audio/{file_name}", "method": "GET", "description": "Get audio file"}
        ]
    }

@app.post("/api/analyze", response_model=dict)
async def analyze_company(request: CompanyRequest, background_tasks: BackgroundTasks):
    """
    Analyze news articles for a company.
    
    This endpoint queues a background task to analyze news articles for the specified company.
    The analysis includes sentiment analysis, comparative analysis, and text-to-speech conversion.
    
    Args:
        request: CompanyRequest object with company_name and num_articles
        background_tasks: FastAPI BackgroundTasks for async processing
        
    Returns:
        Dictionary with task status and instructions
    """
    company_name = request.company_name
    num_articles = request.num_articles
    
    # Queue background task
    background_tasks.add_task(process_news, company_name, num_articles)
    
    return {
        "status": "processing",
        "message": f"Analysis for {company_name} has been queued. Check /api/results/{company_name} for results.",
        "company": company_name
    }

@app.get("/api/results/{company_name}", response_model=Optional[FullAnalysisResponse])
async def get_results(company_name: str):
    """
    Get analysis results for a company.
    
    Args:
        company_name: Name of the company to get results for
        
    Returns:
        FullAnalysisResponse with analysis results if available
    """
    if company_name not in cache:
        raise HTTPException(status_code=404, detail=f"No results found for {company_name}. Submit an analysis request first.")
    
    result = cache[company_name]
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=f"Error processing {company_name}: {result['error']}")
    
    return result

@app.get("/api/companies")
async def list_companies():
    """
    Get list of companies that have been analyzed.
    
    Returns:
        List of company names
    """
    return {
        "companies": list(cache.keys())
    }

@app.get("/audio/{file_name}")
async def get_audio(file_name: str):
    """
    Get audio file for a company analysis.
    
    Args:
        file_name: Name of the audio file
        
    Returns:
        FileResponse with the audio file
    """
    from fastapi.responses import FileResponse
    
    file_path = f"audio_files/{file_name}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Audio file {file_name} not found")
    
    return FileResponse(file_path, media_type="audio/mpeg")

# Define list of predefined companies for the dropdown
@app.get("/api/predefined-companies")
async def get_predefined_companies():
    """
    Get list of predefined companies for the dropdown.
    
    Returns:
        List of company names
    """
    return {
        "companies": [
            "Tesla", "Apple", "Microsoft", "Amazon", "Google", "Meta", 
            "Nvidia", "Netflix", "Uber", "Airbnb", "Twitter", "SpaceX",
            "IBM", "Intel", "AMD", "Coca-Cola", "PepsiCo", "Walmart",
            "Target", "Nike", "Adidas", "Disney", "Sony", "Samsung"
        ]
    }