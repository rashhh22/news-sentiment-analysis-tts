from typing import Dict, Any, List
import logging
from collections import Counter

logger = logging.getLogger(__name__)

class ComparativeAnalyzer:
    """
    Class for performing comparative analysis on sentiment results from multiple articles.
    """
    
    def __init__(self):
        """Initialize the ComparativeAnalyzer instance."""
        pass
    
    def analyze(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comparative analysis on the given articles.
        
        Args:
            articles: List of article dictionaries with sentiment analysis
            
        Returns:
            Dictionary containing comparative analysis results
        """
        if not articles:
            logger.warning("No articles provided for comparative analysis")
            return {
                "sentiment_distribution": {},
                "coverage_differences": [],
                "topic_analysis": {},
                "final_sentiment": "No data available"
            }
        
        try:
            # Count sentiment distributions
            sentiments = [article.get('sentiment', {}).get('sentiment', 'Neutral') for article in articles]
            sentiment_counts = Counter(sentiments)
            
            # Analyze topics
            all_topics = []
            for article in articles:
                all_topics.extend(article.get('topics', []))
            
            topic_counts = Counter(all_topics)
            most_common_topics = topic_counts.most_common(5)
            
            # Find articles with contrasting sentiments for comparison
            positive_articles = [a for a in articles if a.get('sentiment', {}).get('sentiment') == 'Positive']
            negative_articles = [a for a in articles if a.get('sentiment', {}).get('sentiment') == 'Negative']
            neutral_articles = [a for a in articles if a.get('sentiment', {}).get('sentiment') == 'Neutral']
            
            # Generate coverage difference analysis
            coverage_differences = []
            
            # Compare positive vs negative
            if positive_articles and negative_articles:
                pos_article = positive_articles[0]
                neg_article = negative_articles[0]
                
                comparison = {
                    "comparison": f"{pos_article['title']} presents a positive view, while {neg_article['title']} discusses negative aspects.",
                    "impact": "These contrasting viewpoints suggest mixed market reactions or controversial developments."
                }
                coverage_differences.append(comparison)
            
            # Compare by topic focus
            topic_article_map = {}
            for article in articles:
                for topic in article.get('topics', []):
                    if topic not in topic_article_map:
                        topic_article_map[topic] = []
                    topic_article_map[topic].append(article)
            
            for topic, topic_articles in topic_article_map.items():
                if len(topic_articles) >= 2:
                    article1 = topic_articles[0]
                    article2 = topic_articles[1]
                    
                    if article1.get('sentiment', {}).get('sentiment') != article2.get('sentiment', {}).get('sentiment'):
                        comparison = {
                            "comparison": f"Articles about '{topic}' show differing perspectives: {article1['title']} vs {article2['title']}",
                            "impact": f"This suggests the '{topic}' aspect may be a point of contention or uncertainty."
                        }
                        coverage_differences.append(comparison)
            
            # Determine overall sentiment
            if sentiment_counts.get('Positive', 0) > max(sentiment_counts.get('Negative', 0), sentiment_counts.get('Neutral', 0)):
                final_sentiment = "mostly positive"
            elif sentiment_counts.get('Negative', 0) > max(sentiment_counts.get('Positive', 0), sentiment_counts.get('Neutral', 0)):
                final_sentiment = "mostly negative"
            elif sentiment_counts.get('Neutral', 0) > max(sentiment_counts.get('Positive', 0), sentiment_counts.get('Negative', 0)):
                final_sentiment = "generally neutral"
            else:
                final_sentiment = "mixed"
            
            # Topic overlap analysis
            topic_overlap = {}
            if len(articles) >= 2:
                # Find common topics across articles
                common_topics = set()
                for topic, count in topic_counts.items():
                    if count >= 2:
                        common_topics.add(topic)
                
                # Find unique topics for each article
                unique_topics_by_article = {}
                for i, article in enumerate(articles):
                    article_topics = set(article.get('topics', []))
                    other_topics = set()
                    for other_article in articles:
                        if other_article != article:
                            other_topics.update(other_article.get('topics', []))
                    
                    unique_topics = article_topics - other_topics
                    if unique_topics:
                        unique_topics_by_article[f"Article {i+1} ({article['title'][:30]}...)"] = list(unique_topics)
                
                topic_overlap = {
                    "common_topics": list(common_topics),
                    "unique_topics_by_article": unique_topics_by_article
                }
            
            # Calculate average confidence
            confidences = [article.get('sentiment', {}).get('confidence', 0) for article in articles]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Return comprehensive comparative analysis
            return {
                "sentiment_distribution": dict(sentiment_counts),
                "coverage_differences": coverage_differences[:5],  # Limit to top 5 differences
                "topic_analysis": {
                    "most_common_topics": [{"topic": topic, "count": count} for topic, count in most_common_topics],
                    "topic_overlap": topic_overlap
                },
                "final_sentiment": f"The news coverage is {final_sentiment} with an average confidence of {avg_confidence:.2f}."
            }
            
        except Exception as e:
            logger.error(f"Error in comparative analysis: {str(e)}")
            return {
                "sentiment_distribution": {},
                "coverage_differences": [],
                "topic_analysis": {},
                "final_sentiment": "Error in analysis",
                "error": str(e)
            }