from typing import List, Dict, Any
import logging
from utils import search_news_articles, extract_article_content, summarize_text, extract_topics

logger = logging.getLogger(__name__)

class NewsExtractor:
    """
    Class for extracting news articles related to a given company.
    """
    
    def __init__(self):
        """Initialize the NewsExtractor instance."""
        pass
    
    def fetch_news(self, company_name: str, num_articles: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch news articles related to the given company.
        
        Args:
            company_name: Name of the company to search for
            num_articles: Number of articles to retrieve
            
        Returns:
            List of dictionaries containing article data
        """
        logger.info(f"Fetching news for company: {company_name}")
        
        # Search for news articles
        article_links = search_news_articles(company_name, num_articles)
        
        if not article_links:
            logger.warning(f"No news articles found for {company_name}")
            return []
        
        # Extract full content from each article
        articles = []
        for link_data in article_links:
            try:
                logger.info(f"Extracting content from: {link_data['url']}")
                
                article_data = extract_article_content(link_data['url'])
                
                if not article_data.get('content'):
                    logger.warning(f"No content extracted from {link_data['url']}")
                    continue
                
                # Create a summary if the content is too long
                summary = summarize_text(article_data['content'])
                
                # Extract topics
                topics = extract_topics(article_data['content'])
                
                articles.append({
                    "title": article_data.get('title', link_data.get('snippet', 'Untitled')),
                    "url": link_data['url'],
                    "source": link_data.get('source', 'Unknown'),
                    "date": article_data.get('date', link_data.get('time', 'Unknown')),
                    "content": article_data['content'],
                    "summary": summary,
                    "topics": topics
                })
                
                if len(articles) >= num_articles:
                    break
                    
            except Exception as e:
                logger.error(f"Error processing article {link_data['url']}: {str(e)}")
                continue
        
        logger.info(f"Successfully extracted {len(articles)} articles for {company_name}")
        return articles