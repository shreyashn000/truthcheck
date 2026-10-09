from flask import Flask, render_template, request, jsonify
import os
import joblib
import requests

app = Flask(__name__)


# --------------------------------------------------
# LOAD MACHINE LEARNING MODEL
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR, "model", "fake_news_model.pkl"
)
VECTORIZER_PATH = os.path.join(
    BASE_DIR, "model", "tfidf_vectorizer.pkl"
)

model = None
vectorizer = None

if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)


GOOGLE_FACTCHECK_API_URL = (
    "https://factchecktools.googleapis.com/v1alpha1/claims:search"
)




def search_fact_checks(news):
    api_key = os.environ.get("GOOGLE_FACTCHECK_API_KEY")

    if not api_key:
        raise RuntimeError("Google Fact Check API key is missing.")

    # Try the full text first, then a shorter query if needed.
    words = news.split()
    queries = [news[:200]]

    if len(words) > 6:
        queries.append(" ".join(words[:6]))

    seen_urls = set()
    matches = []

    for query in queries:
        response = requests.get(
            GOOGLE_FACTCHECK_API_URL,
            params={
                "query": query,
                "key": api_key,
                "languageCode": "en",
                "pageSize": 5
            },
            timeout=15
        )

        if not response.ok:
            app.logger.error(
                "Fact Check API error %s: %s",
                response.status_code,
                response.text
            )
            raise RuntimeError("Google Fact Check API request failed.")

        data = response.json()
        print("Fact-check query:", query)
        print("Matching claims:", len(data.get("claims", [])))

        for claim in data.get("claims", []):
            for review in claim.get("claimReview", []):
                url = review.get("url", "")

                if url and url in seen_urls:
                    continue

                if url:
                    seen_urls.add(url)

                matches.append({
                    "claim": claim.get("text", ""),
                    "publisher": review.get(
                        "publisher", {}
                    ).get("name", "Unknown publisher"),
                    "rating": review.get(
                        "textualRating", "Rating not provided"
                    ),
                    "title": review.get(
                        "title", "Fact-check review"
                    ),
                    "url": url,
                    "review_date": review.get("reviewDate", "")
                })

        if matches:
            break

    return matches[:5]



# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# DETECT NEWS
# --------------------------------------------------

@app.route("/detect")
def detect():
    return render_template("detect.html")


# --------------------------------------------------
# HOW IT WORKS
# --------------------------------------------------

@app.route("/how-it-works")
def how_it_works():
    return render_template("how-it-works.html")


# --------------------------------------------------
# MEDIA LITERACY
# --------------------------------------------------

@app.route("/media-literacy")
def media_literacy():
    return render_template("media-literacy.html")


# --------------------------------------------------
# ABOUT
# --------------------------------------------------

@app.route("/about")
def about():
    return render_template("about.html")


# --------------------------------------------------
# NEWS PREDICTION
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    news = data.get("news", "")

    if not isinstance(news, str):
        return jsonify({
            "success": False,
            "error": "News must be text."
        }), 400

    news = news.strip()

    if not news:
        return jsonify({
            "success": False,
            "error": "Please enter a news article or headline."
        }), 400

    if len(news.split()) < 5:
        return jsonify({
            "success": False,
            "error": "Please enter at least 5 words."
        }), 400

    # Search published fact-check reviews first.
    reviews = search_fact_checks(news)

    # Keep ML prediction as a secondary signal.
    ml_signal = "UNAVAILABLE"
    ml_confidence = None

    if model is not None and vectorizer is not None:
        news_vector = vectorizer.transform([news])
        prediction = model.predict(news_vector)[0]
        probabilities = model.predict_proba(news_vector)[0]

        ml_confidence = round(
            float(max(probabilities)) * 100, 2
        )

        if ml_confidence < 65:
            ml_signal = "UNCERTAIN"
        elif prediction == 0:
            ml_signal = "LIKELY FAKE"
        else:
            ml_signal = "LIKELY REAL"

    # A published review is evidence, not an infallible verdict.
    if reviews:
        return jsonify({
            "success": True,
            "result": "FACT-CHECK FOUND",
            "confidence": None,
            "advice": (
                "A published fact-check review was found. "
                "Read the review and its evidence before deciding "
                "whether the claim is accurate."
            ),
            "fact_checks": reviews,
            "ml_signal": ml_signal,
            "ml_confidence": ml_confidence
        })

    # No matching review means the claim remains unverified.
    return jsonify({
        "success": True,
        "result": "UNVERIFIED",
        "confidence": None,
        "advice": (
            "No matching published fact-check was found in this search. "
            "This does not mean the news is fake or real. Check reliable "
            "sources and the original evidence before sharing."
        ),
        "fact_checks": [],
        "ml_signal": ml_signal,
        "ml_confidence": ml_confidence
    })


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)