from flask import Flask, render_template, request, jsonify
import os
import joblib

app = Flask(__name__)


# --------------------------------------------------
# LOAD MACHINE LEARNING MODEL
# --------------------------------------------------

MODEL_PATH = "model/fake_news_model.pkl"
VECTORIZER_PATH = "model/tfidf_vectorizer.pkl"

model = None
vectorizer = None

if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)


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

    global model, vectorizer

    if model is None or vectorizer is None:
        return jsonify({
            "success": False,
            "error": "Machine Learning model has not been trained yet."
        }), 500

    data = request.get_json()

    if not data or "news" not in data:
        return jsonify({
            "success": False,
            "error": "No news text was provided."
        }), 400

    news = data["news"].strip()

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

    # Convert news text into TF-IDF features
    news_vector = vectorizer.transform([news])

    # Make prediction
    prediction = model.predict(news_vector)[0]

    # Get probability
    probabilities = model.predict_proba(news_vector)[0]

    confidence = max(probabilities) * 100
    confidence = round(confidence, 2)

    # Classification
    if confidence < 65:

        result = "UNCERTAIN"

        advice = (
            "The model is not sufficiently confident about this result. "
            "Verify the information using reliable sources before sharing it."
        )

    elif prediction == 0:

        result = "LIKELY FAKE"

        advice = (
            "The model found patterns associated with fake-news examples "
            "in its training data. This does not prove that the claim is false. "
            "Check the original source, date and supporting evidence."
        )

    else:

        result = "LIKELY REAL"

        advice = (
            "The model found patterns associated with real-news examples "
            "in its training data. This does not prove that the claim is true. "
            "Check the original source and supporting evidence."
        )

    return jsonify({
        "success": True,
        "result": result,
        "confidence": confidence,
        "advice": advice
    })


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)