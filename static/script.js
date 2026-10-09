javascript
/* ==================================================
   WORD COUNTER
================================================== */

const newsInput = document.getElementById("newsInput");
const wordCount = document.getElementById("wordCount");

if (newsInput && wordCount) {
    newsInput.addEventListener("input", function () {
        const text = newsInput.value.trim();
        const words = text ? text.split(/\s+/).length : 0;

        wordCount.textContent =
            words + (words === 1 ? " word" : " words");
    });
}


/* ==================================================
   CHECK NEWS
================================================== */

async function checkNews() {
    const newsInput = document.getElementById("newsInput");
    const checkButton = document.getElementById("checkButton");
    const loading = document.getElementById("loading");
    const result = document.getElementById("result");

    const resultText = document.getElementById("resultText");
    const confidenceText = document.getElementById("confidenceText");
    const confidenceFill = document.getElementById("confidenceFill");
    const adviceText = document.getElementById("adviceText");

    if (!newsInput || !checkButton || !loading || !result) {
        console.error("Required detector element is missing.");
        return;
    }

    const news = newsInput.value.trim();

    if (!news) {
        alert("Please enter a news headline or article.");
        newsInput.focus();
        return;
    }

    if (news.split(/\s+/).length < 5) {
        alert("Please enter at least 5 words.");
        newsInput.focus();
        return;
    }

    loading.style.display = "block";
    result.style.display = "none";
    checkButton.disabled = true;

    try {
        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ news: news })
        });

        const responseText = await response.text();

        let data;

        try {
            data = JSON.parse(responseText);
        } catch (error) {
            console.error("Server returned HTML or invalid JSON:", responseText);
            throw new Error(
                `Server returned a non-JSON response (HTTP ${response.status}). Check the Flask terminal.`
            );
        }

        if (!response.ok || !data.success) {
            throw new Error(
                data.error || "Unable to analyze the news."
            );
        }

        if (resultText) {
            resultText.textContent = data.result;
        }

        if (confidenceText) {
            if (data.confidence !== null &&
                data.confidence !== undefined) {
                confidenceText.textContent =
                    data.confidence + "%";
            } else {
                confidenceText.textContent =
                    "No verified confidence score";
            }
        }

        if (confidenceFill) {
            const confidence =
                Number(data.confidence);

            confidenceFill.style.width =
                Number.isFinite(confidence)
                    ? Math.max(0, Math.min(100, confidence)) + "%"
                    : "0%";
        }

        if (adviceText) {
            adviceText.textContent = data.advice || "";
        }

        result.className = "result";

        if (data.result === "LIKELY REAL") {
            result.classList.add("likely-real");
        } else if (data.result === "LIKELY FAKE") {
            result.classList.add("likely-fake");
        } else {
            result.classList.add("uncertain");
        }

        /* FACT-CHECK REVIEWS */

        let reviewsContainer =
            document.getElementById("factCheckResults");

        if (!reviewsContainer) {
            reviewsContainer = document.createElement("div");
            reviewsContainer.id = "factCheckResults";
            reviewsContainer.style.marginTop = "20px";

            if (adviceText && adviceText.parentElement) {
                adviceText.parentElement.appendChild(
                    reviewsContainer
                );
            } else {
                result.appendChild(reviewsContainer);
            }
        }

        reviewsContainer.replaceChildren();

        const heading = document.createElement("h3");
        heading.textContent = "Published Fact-Check Reviews";
        reviewsContainer.appendChild(heading);

        if (Array.isArray(data.fact_checks) &&
            data.fact_checks.length > 0) {

            data.fact_checks.forEach(function (review) {
                const card = document.createElement("article");
                card.style.padding = "14px";
                card.style.marginTop = "12px";
                card.style.border = "1px solid #ddd";
                card.style.borderRadius = "8px";

                const title = document.createElement("h4");
                title.textContent =
                    review.title || "Fact-check review";
                card.appendChild(title);

                const claim = document.createElement("p");
                claim.textContent =
                    "Claim reviewed: " +
                    (review.claim || "Not provided");
                card.appendChild(claim);

                const publisher = document.createElement("p");
                publisher.textContent =
                    "Publisher: " +
                    (review.publisher || "Unknown");
                card.appendChild(publisher);

                const rating = document.createElement("p");
                rating.textContent =
                    "Publisher's rating: " +
                    (review.rating || "Not provided");
                card.appendChild(rating);

                if (review.review_date) {
                    const date = document.createElement("p");
                    date.textContent =
                        "Review date: " + review.review_date;
                    card.appendChild(date);
                }

                if (review.url) {
                    try {
                        const linkUrl = new URL(review.url);

                        if (linkUrl.protocol === "https:" ||
                            linkUrl.protocol === "http:") {
                            const link =
                                document.createElement("a");

                            link.href = linkUrl.href;
                            link.textContent =
                                "Read original fact-check";
                            link.target = "_blank";
                            link.rel = "noopener noreferrer";
                            card.appendChild(link);
                        }
                    } catch (error) {
                        console.warn(
                            "Invalid fact-check URL."
                        );
                    }
                }

                reviewsContainer.appendChild(card);
            });

        } else {
            const noReviews = document.createElement("p");
            noReviews.textContent =
                "No matching published fact-check was found. " +
                "This does not prove the news is true or false.";
            reviewsContainer.appendChild(noReviews);
        }

        /* DISPLAY ML SIGNAL SEPARATELY */

        if (data.ml_signal) {
            const mlInfo = document.createElement("p");
            mlInfo.style.marginTop = "16px";
            mlInfo.textContent =
                "Secondary AI model signal: " +
                data.ml_signal +
                (data.ml_confidence !== null &&
                 data.ml_confidence !== undefined
                    ? " (" + data.ml_confidence +
                      "% model confidence)"
                    : "");

            reviewsContainer.appendChild(mlInfo);
        }

        result.style.display = "block";

        setTimeout(function () {
            result.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }, 100);

    } catch (error) {
        console.error(error);
        alert("Error: " + error.message);
    } finally {
        loading.style.display = "none";
        checkButton.disabled = false;
    }
}


/* ==================================================
   CHECK ANOTHER NEWS
================================================== */

function checkAnotherNews() {
    const newsInput =
        document.getElementById("newsInput");
    const result =
        document.getElementById("result");
    const wordCount =
        document.getElementById("wordCount");
    const reviews =
        document.getElementById("factCheckResults");

    if (newsInput) {
        newsInput.value = "";
        newsInput.focus();
    }

    if (wordCount) {
        wordCount.textContent = "0 words";
    }

    if (result) {
        result.style.display = "none";
        result.className = "result";
    }

    if (reviews) {
        reviews.replaceChildren();
    }

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


/* ==================================================
   SAMPLE NEWS
================================================== */

function loadSample(type) {
    const input = document.getElementById("newsInput");

    if (!input) return;

    if (type === "fake") {
        input.value =
            "Government announces that every citizen will receive free smartphones tomorrow. Share this message with all your contacts immediately to claim your benefit.";
    } else {
        input.value =
            "The government announced a new public initiative today, with officials stating that the programme will be implemented in phases across several regions.";
    }

    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.focus();
}


/* ==================================================
   MOBILE NAVIGATION
================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const menuToggle =
        document.getElementById("menuToggle");
    const navLinks =
        document.getElementById("navLinks");

    if (!menuToggle || !navLinks) return;

    menuToggle.addEventListener("click", function () {
        navLinks.classList.toggle("open");

        const isOpen = navLinks.classList.contains("open");

        menuToggle.textContent = isOpen ? "×" : "☰";
        menuToggle.setAttribute(
            "aria-label",
            isOpen ? "Close menu" : "Open menu"
        );
    });

    navLinks.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
            navLinks.classList.remove("open");
            menuToggle.textContent = "☰";
            menuToggle.setAttribute(
                "aria-label",
                "Open menu"
            );
        });
    });
});