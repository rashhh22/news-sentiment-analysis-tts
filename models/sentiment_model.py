from typing import Dict, Any, List, Tuple
import logging
from transformers import pipeline
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download NLTK resources if not already available
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Class for performing sentiment analysis on news articles.
    """
    
    def __init__(self, use_transformer: bool = True):
        """
        Initialize the SentimentAnalyzer instance.
        
        Args:
            use_transformer: Whether to use the Hugging Face transformer model.
                            Falls back to NLTK's VADER if False or if transformer fails.
        """
        self.use_transformer = use_transformer
        
        # Initialize VADER sentiment analyzer as fallback
        self.vader = SentimentIntensityAnalyzer()
        
        # Initialize transformer model if requested
        self.transformer = None
        if use_transformer:
            try:
                logger.info("Loading sentiment analysis transformer model")
                self.transformer = pipeline("sentiment-analysis")
                logger.info("Transformer model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load transformer model: {str(e)}")
                logger.info("Falling back to VADER sentiment analyzer")
                self.use_transformer = False
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of the given text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary containing sentiment label and scores
        """
        # Use a sample of text if it's too long
        sample_text = text[:1000] if len(text) > 1000 else text
        
        try:
            if self.use_transformer and self.transformer:
                # Use transformer model
                result = self.transformer(sample_text)[0]
                
                # Map to standard format
                sentiment = result['label'].lower()
                score = result['score']
                
                if sentiment == 'positive':
                    sentiment_label = 'Positive'
                elif sentiment == 'negative':
                    sentiment_label = 'Negative'
                else:
                    sentiment_label = 'Neutral'
                
                return {
                    "sentiment": sentiment_label,
                    "confidence": score,
                    "details": {
                        "original_label": result['label'],
                        "original_score": result['score']
                    }
                }
                
            else:
                # Use VADER
                scores = self.vader.polarity_scores(sample_text)
                
                # Determine sentiment based on compound score
                if scores['compound'] >= 0.05:
                    sentiment_label = 'Positive'
                elif scores['compound'] <= -0.05:
                    sentiment_label = 'Negative'
                else:
                    sentiment_label = 'Neutral'
                
                return {
                    "sentiment": sentiment_label,
                    "confidence": abs(scores['compound']),
                    "details": {
                        "positive": scores['pos'],
                        "negative": scores['neg'],
                        "neutral": scores['neu'],
                        "compound": scores['compound']
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            
            # Fallback to simple approach
            positive_words = ['good', 'great', 'excellent', 'positive', 'profit', 'growth', 'success', 'increase']
            negative_words = ['bad', 'poor', 'negative', 'loss', 'decline', 'failure', 'decrease', 'concern']
            
            text_lower = text.lower()
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                sentiment_label = 'Positive'
                confidence = min(0.7, pos_count / (pos_count + neg_count + 1))
            elif neg_count > pos_count:
                sentiment_label = 'Negative'
                confidence = min(0.7, neg_count / (pos_count + neg_count + 1))
            else:
                sentiment_label = 'Neutral'
                confidence = 0.5
            
            return {
                "sentiment": sentiment_label,
                "confidence": confidence,
                "details": {
                    "error": str(e),
                    "fallback": True
                }
            }
    
    def analyze_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze the sentiment of a list of articles.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            The same list with sentiment analysis added to each article
        """
        analyzed_articles = []
        
        for article in articles:
            try:
                # Analyze the article content
                sentiment_result = self.analyze_sentiment(article['content'])
                
                # Add sentiment analysis to the article
                article_with_sentiment = article.copy()
                article_with_sentiment['sentiment'] = sentiment_result
                
                analyzed_articles.append(article_with_sentiment)
                
            except Exception as e:
                logger.error(f"Error analyzing article {article.get('title', 'Unknown')}: {str(e)}")
                # Include the article without sentiment analysis
                analyzed_articles.append(article)
        
        return analyzed_articles