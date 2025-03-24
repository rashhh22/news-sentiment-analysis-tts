import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean and normalize text data."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()

def extract_article_content(url: str) -> Dict[str, Any]:
    """
    Extract content from a news article URL using BeautifulSoup.
    
    Args:
        url: URL of the news article
        
    Returns:
        Dictionary containing title, content, and publication date
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = ""
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            title = clean_text(title_tag.get_text())
        
        # Extract main content
        content = ""
        # Look for common article content containers
        article_tags = soup.find('article') or soup.find('div', class_=re.compile(r'article|content|story'))
        if article_tags:
            paragraphs = article_tags.find_all('p')
            content = ' '.join([clean_text(p.get_text()) for p in paragraphs])
        else:
            # Fallback to all paragraphs in the page
            paragraphs = soup.find_all('p')
            content = ' '.join([clean_text(p.get_text()) for p in paragraphs])
        
        # Extract publication date
        date = ""
        date_tag = soup.find('time') or soup.find('meta', property='article:published_time')
        if date_tag:
            if date_tag.name == 'time':
                date = date_tag.get('datetime') or date_tag.get_text()
            else:
                date = date_tag.get('content', '')
        
        return {
            "title": title,
            "content": content,
            "date": date,
            "url": url
        }
    
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return {
            "title": "",
            "content": "",
            "date": "",
            "url": url,
            "error": str(e)
        }

def search_news_articles(company_name: str, num_articles: int = 10) -> List[Dict[str, Any]]:
    """
    Search for news articles related to a company using Google News.
    
    Args:
        company_name: Name of the company to search for
        num_articles: Number of articles to retrieve
        
    Returns:
        List of dictionaries containing article URLs and metadata
    """
    try:
        # Prepare search query
        query = f"{company_name} news"
        search_url = f"https://www.google.com/search?q={query}&tbm=nws"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract news article links
        article_links = []
        news_divs = soup.find_all('div', class_='SoaBEf')
        
        for div in news_divs:
            if len(article_links) >= num_articles:
                break
                
            link_tag = div.find('a')
            if not link_tag:
                continue
                
            url = link_tag.get('href')
            if url and url.startswith('/url?q='):
                # Clean Google redirect URL
                url = url.split('/url?q=')[1].split('&sa=')[0]
                
            # Skip non-http links and Google News links
            if not (url.startswith('http') and 'google.com' not in url):
                continue
                
            # Extract snippet
            snippet = ""
            snippet_div = div.find('div', class_='GI74Re')
            if snippet_div:
                snippet = clean_text(snippet_div.get_text())
                
            # Extract source and time
            source = ""
            time = ""
            source_div = div.find('div', class_='CEMjEf')
            if source_div:
                source_text = source_div.get_text()
                if ' · ' in source_text:
                    source, time = source_text.split(' · ', 1)
                else:
                    source = source_text
            
            article_links.append({
                "url": url,
                "snippet": snippet,
                "source": source,
                "time": time
            })
        
        return article_links
        
    except Exception as e:
        logger.error(f"Error searching news for {company_name}: {str(e)}")
        return []
    
def summarize_text(text: str, max_length: int = 200) -> str:
    """
    Create a simple extractive summary of the text.
    
    Args:
        text: The text to summarize
        max_length: Maximum length of the summary in characters
        
    Returns:
        Summarized text
    """
    if not text or len(text) <= max_length:
        return text
    
    # Simple extractive summarization - take first few sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    summary = ""
    
    for sentence in sentences:
        if len(summary) + len(sentence) > max_length:
            break
        summary += sentence + " "
    
    return summary.strip()

def extract_topics(text: str, num_topics: int = 3) -> List[str]:
    """
    Extract key topics from the text using a simple keyword extraction approach.
    
    Args:
        text: The text to analyze
        num_topics: Number of topics to extract
        
    Returns:
        List of topic keywords
    """
    # This is a simple keyword extraction implementation
    # In a production environment, you might want to use more advanced NLP techniques
    
    # Remove common stopwords
    stopwords = ['the', 'and', 'a', 'in', 'to', 'of', 'for', 'on', 'with', 'as', 'at', 'by', 'an', 'is', 'was', 'were', 'be', 'been']
    words = text.lower().split()
    words = [word for word in words if word not in stopwords and len(word) > 3]
    
    # Count word frequencies
    word_freq = {}
    for word in words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    # Return top keywords
    topics = [word[0].capitalize() for word in sorted_words[:num_topics]]
    return topics