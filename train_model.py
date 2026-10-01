import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# ==========================================
# FILE PATHS
# ==========================================

FAKE_PATH = "dataset/Fake.csv"
TRUE_PATH = "dataset/True.csv"

MODEL_DIR = "model"

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "fake_news_model.pkl"
)

VECTORIZER_PATH = os.path.join(
    MODEL_DIR,
    "tfidf_vectorizer.pkl"
)


# ==========================================
# CHECK DATASET
# ==========================================

if not os.path.exists(FAKE_PATH):
    raise FileNotFoundError(
        "Fake.csv was not found inside dataset folder."
    )

if not os.path.exists(TRUE_PATH):
    raise FileNotFoundError(
        "True.csv was not found inside dataset folder."
    )


# ==========================================
# LOAD DATA
# ==========================================

print("\nLoading dataset...")

fake = pd.read_csv(FAKE_PATH)
true = pd.read_csv(TRUE_PATH)

print("Fake articles:", len(fake))
print("Real articles:", len(true))


# ==========================================
# ADD LABELS
# ==========================================

fake["label"] = 0
true["label"] = 1


# ==========================================
# COMBINE DATA
# ==========================================

data = pd.concat(
    [fake, true],
    ignore_index=True
)


# ==========================================
# CLEAN TEXT
# ==========================================

data["title"] = data["title"].fillna("")
data["text"] = data["text"].fillna("")

data["content"] = (
    data["title"] + " " + data["text"]
)


# Remove empty articles

data = data[
    data["content"].str.strip() != ""
]


# Remove duplicate articles

data = data.drop_duplicates(
    subset=["content"]
)


# Shuffle

data = data.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


print("\nTotal articles:", len(data))

print("\nClass distribution:")
print(data["label"].value_counts())


# ==========================================
# FEATURES AND LABEL
# ==========================================

X = data["content"]
y = data["label"]


# ==========================================
# TRAIN TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTraining articles:", len(X_train))
print("Testing articles:", len(X_test))


# ==========================================
# TF-IDF
# ==========================================

print("\nCreating TF-IDF features...")

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_df=0.7,
    max_features=100000
)


X_train_tfidf = vectorizer.fit_transform(X_train)

X_test_tfidf = vectorizer.transform(X_test)


print(
    "TF-IDF training shape:",
    X_train_tfidf.shape
)


# ==========================================
# LOGISTIC REGRESSION
# ==========================================

print("\nTraining Logistic Regression model...")

model = LogisticRegression(
    max_iter=1000
)

model.fit(
    X_train_tfidf,
    y_train
)


# ==========================================
# PREDICTION
# ==========================================

print("\nEvaluating model...")

y_pred = model.predict(
    X_test_tfidf
)


# ==========================================
# METRICS
# ==========================================

accuracy = accuracy_score(
    y_test,
    y_pred
)


print("\n====================================")
print("MODEL RESULTS")
print("====================================")

print(
    f"\nAccuracy: {accuracy * 100:.2f}%"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Fake",
            "Real"
        ]
    )
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ==========================================
# SAVE MODEL
# ==========================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


print("\nSaving model...")

joblib.dump(
    model,
    MODEL_PATH
)


joblib.dump(
    vectorizer,
    VECTORIZER_PATH
)


# ==========================================
# VERIFY FILES
# ==========================================

print("\nChecking saved files...")

if os.path.exists(MODEL_PATH):
    model_size = os.path.getsize(MODEL_PATH)

    print(
        f"Model saved: {MODEL_PATH}"
    )

    print(
        f"Model file size: {model_size:,} bytes"
    )

else:
    raise RuntimeError(
        "Model file was not created."
    )


if os.path.exists(VECTORIZER_PATH):
    vectorizer_size = os.path.getsize(
        VECTORIZER_PATH
    )

    print(
        f"Vectorizer saved: {VECTORIZER_PATH}"
    )

    print(
        f"Vectorizer file size: {vectorizer_size:,} bytes"
    )

else:
    raise RuntimeError(
        "Vectorizer file was not created."
    )


print("\n====================================")
print("TRAINING COMPLETED SUCCESSFULLY")
print("====================================")