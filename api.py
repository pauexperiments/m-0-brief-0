from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
from langdetect import detect_langs
from nltk.sentiment import SentimentIntensityAnalyzer as ENSentimentIntensityAnalyzer
from vaderSentiment_fr.vaderSentiment import SentimentIntensityAnalyzer as FRSentimentIntensityAnalyzer


sia_en = ENSentimentIntensityAnalyzer()
sia_fr = FRSentimentIntensityAnalyzer()

app = FastAPI()


class TextRequest(BaseModel):
    text: str
    language: Literal["fr", "en"] | None = None


class Sentiment(BaseModel):
    negative: float = 0.0
    neutral: float  = 0.0
    positive: float = 0.0
    compound: float = 0.0


class SentimentResponse(BaseModel):
    requested_text: str
    requested_language: Literal["fr", "en"] | None = None
    language: Literal["fr", "en"] = "en"
    sentiment: Sentiment


@app.post("/sentiment/", response_model=SentimentResponse)
async def analyse_sentiment(text_request: TextRequest):

    text = text_request.text
    language = text_request.language
    
    # Detect language if not provided
    if language is None:
        langs = detect_langs(text)
        for lang in langs:
            if lang.lang in ["fr", "en"]:
                language= lang.lang
                break

    # Default to English if no valid language detected
    if language is None:
        language = "en"

    # Sentiment
    if language == "en":
        scores = sia_en.polarity_scores(text)
    elif language == "fr":
        scores = sia_fr.polarity_scores(text)

    sentiment = Sentiment(
        negative = scores['neg'],
        neutral  = scores['neu'],
        positive = scores['pos'],
        compound = scores['compound']
    )

    # Return
    return SentimentResponse(
        requested_text=text_request.text,
        requested_language=text_request.language,
        language=language,
        sentiment=sentiment,
    )


