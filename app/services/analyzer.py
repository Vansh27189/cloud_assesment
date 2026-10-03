"""NLP text and sentiment analysis service."""

import re
from datetime import datetime, timezone
from typing import List, Tuple
from app.models import KeywordItem, SentimentAnalysisResult

# Curated positive and negative lexicon for deterministic sentiment analysis
POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "wonderful", "fantastic", "terrific",
    "awesome", "love", "loved", "lovely", "best", "perfect", "superb", "brilliant",
    "outstanding", "positive", "happy", "delighted", "smooth", "fast", "reliable",
    "scalable", "secure", "success", "successful", "impressive", "clean", "easy",
    "efficient", "stable", "innovative", "seamless", "exceptional", "valuable"
}

NEGATIVE_WORDS = {
    "bad", "terrible", "horrible", "awful", "poor", "worst", "hate", "hated",
    "broken", "slow", "sluggish", "bug", "bugs", "buggy", "error", "errors",
    "fail", "failed", "failing", "failure", "crash", "crashed", "negative",
    "unhappy", "difficult", "frustrating", "unstable", "vulnerable", "insecure",
    "defect", "flawed", "useless", "disaster", "down", "outage", "bottleneck"
}

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with",
    "is", "was", "are", "were", "be", "been", "it", "this", "that", "of", "from",
    "by", "as", "if", "so", "than", "too", "very", "can", "will", "just", "we", "i",
    "you", "he", "she", "they", "them", "my", "our", "your"
}


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric words."""
    return re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())


def analyze_sentiment(text: str, instance_id: str) -> SentimentAnalysisResult:
    """Perform sentiment analysis, text metrics, and keyword extraction."""
    tokens = tokenize(text)
    word_count = len(tokens)
    char_count = len(text)

    pos_hits = sum(1 for w in tokens if w in POSITIVE_WORDS)
    neg_hits = sum(1 for w in tokens if w in NEGATIVE_WORDS)

    total_hits = pos_hits + neg_hits
    if total_hits > 0:
        polarity = (pos_hits - neg_hits) / total_hits
    else:
        polarity = 0.0

    # Determine sentiment label with confidence margins
    if polarity >= 0.15:
        sentiment_label = "POSITIVE"
    elif polarity <= -0.15:
        sentiment_label = "NEGATIVE"
    else:
        sentiment_label = "NEUTRAL"

    # Extract keywords (excluding stop words)
    filtered = [w for w in tokens if w not in STOP_WORDS]
    word_counts: dict[str, int] = {}
    for w in filtered:
        word_counts[w] = word_counts.get(w, 0) + 1

    sorted_keywords = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    keyword_items = [KeywordItem(word=k, count=v) for k, v in sorted_keywords]

    # Estimated read time (average 200 words per minute -> ~3.33 words/sec)
    read_time = round(word_count / 3.33, 2) if word_count > 0 else 0.0

    preview = (text[:120] + "...") if len(text) > 120 else text

    return SentimentAnalysisResult(
        text_preview=preview,
        polarity_score=round(polarity, 3),
        sentiment_label=sentiment_label,
        word_count=word_count,
        char_count=char_count,
        estimated_read_time_seconds=read_time,
        keywords=keyword_items,
        processed_by_instance=instance_id,
        processed_at=datetime.now(timezone.utc).isoformat()
    )
