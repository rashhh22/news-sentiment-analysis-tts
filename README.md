# News Summarization and Text-to-Speech Application

This application extracts news articles for a given company, performs sentiment analysis, conducts comparative analysis, and generates a Hindi Text-to-Speech (TTS) summary.

## Features

- **News Extraction**: Extracts news articles related to a company using BeautifulSoup
- **Sentiment Analysis**: Analyzes sentiment (positive, negative, neutral) for each article
- **Comparative Analysis**: Compares sentiment and topics across articles
- **Hindi TTS**: Converts the summarized content to Hindi speech
- **Web Interface**: Simple Streamlit interface for user interaction
- **API Support**: Comprehensive API for all functionalities

## Demo

[Link to Hugging Face Spaces deployment]

## Quick Start

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/news-summarization-tts.git
   cd news-summarization-tts
   ```

2. Create a virtual environment (Optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   streamlit run app.py
   ```

5. Access the application at http://localhost:8501

### Using the API

1. Start the API server:
   ```
   python api.py
   ```

2. The API will be available at http://localhost:5000

#### API Endpoints:

- `GET /api/news?company_name=Tesla`: Fetch news articles
- `POST /api/sentiment`: Analyze sentiment (requires article content in JSON body)
- `POST /api/comparative-analysis`: Perform comparative analysis (requires articles in JSON body)
- `POST /api/tts`: Generate Hindi TTS (requires text in JSON body)
- `GET /api/full-analysis?company_name=Tesla`: Perform complete analysis workflow

Example Postman API request:
```
GET http://localhost:5000/api/news?company_name=Tesla
```

## Project Structure

```
news-summarization-tts/
├── app.py                  # Main Streamlit application
├── api.py                  # API endpoints
├── utils.py                # Utility functions
├── models/                 # Directory for model files
│   ├── sentiment_model.py  # Sentiment analysis model
│   ├── summarization.py    # Text summarization
│   ├── tts_model.py        # Text-to-speech model for Hindi
│   └── __init__.py
├── services/               # Business logic
│   ├── news_extractor.py   # News extraction using BeautifulSoup
│   ├── sentiment_analyzer.py  # Sentiment analysis service
│   ├── comparative_analyzer.py  # Comparative analysis
│   ├── tts_service.py      # Text-to-speech service
│   └── __init__.py
└── requirements.txt        # Dependencies
```

## Models Used

### Sentiment Analysis

The application uses two approaches for sentiment analysis:
1. **Transformer-based Model**: Using DistilBERT fine-tuned on sentiment analysis tasks
2. **NLTK VADER**: As a fallback option when transformer model is unavailable

### Text-to-Speech

For Hindi TTS, the application uses:
1. **Local TTS Model**: Facebook's MMS-TTS-HIN model (when GPU is available)
2. **Google TTS (gTTS)**: As a fallback option

## Assumptions & Limitations

- **News Sources**: The application focuses on news sources that can be scraped with BeautifulSoup (non-JS websites)
- **Language Support**: Primary focus on English for extraction and Hindi for TTS
- **Processing Speed**: Processing time depends on the number of articles and internet connection speed
- **Content Length**: TTS has a limit on the amount of text it can process at once (5000 characters)

## Development

### Running Tests

```
python -m pytest tests/
```

### Adding New Features

1. Create a new service in the services directory
2. Implement the API endpoint in api.py
3. Update the Streamlit interface in app.py

## Deployment

### Hugging Face Spaces

1. Create a new Space on Hugging Face
2. Choose Streamlit as the SDK
3. Upload the project files
4. Set the requirements.txt file for dependencies

## Troubleshooting

Common issues and solutions:

1. **No articles found**: Try a different company name or check internet connection
2. **TTS not working**: Ensure you have internet access for gTTS or a GPU for local model
3. **Slow performance**: Reduce the number of articles to analyze by modifying the limit parameter

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
