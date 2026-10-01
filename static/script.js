/* ==================================================
   WORD COUNTER
================================================== */

const newsInput = document.getElementById("newsInput");
const wordCount = document.getElementById("wordCount");

if (newsInput && wordCount) {

    newsInput.addEventListener("input", function () {

        const text = newsInput.value.trim();

        if (!text) {
            wordCount.textContent = "0 words";
            return;
        }

        const words = text.split(/\s+/).length;

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
    const confidenceText =
        document.getElementById("confidenceText");

    const confidenceFill =
        document.getElementById("confidenceFill");

    const adviceText =
        document.getElementById("adviceText");


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


    const words = news.split(/\s+/);


    if (words.length < 5) {

        alert("Please enter at least 5 words.");

        newsInput.focus();

        return;
    }


    /* SHOW LOADING */

    loading.style.display = "block";

    result.style.display = "none";

    checkButton.disabled = true;


    try {

        const response = await fetch("/predict", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                news: news
            })

        });


        const data = await response.json();


        if (!response.ok || !data.success) {

            throw new Error(
                data.error || "Unable to analyze the news."
            );

        }


        /* RESULT */

        if (resultText) {

            resultText.textContent =
                data.result;

        }


        /* CONFIDENCE */

        if (confidenceText) {

            confidenceText.textContent =
                data.confidence + "%";

        }


        if (confidenceFill) {

            confidenceFill.style.width =
                data.confidence + "%";

        }


        /* ADVICE */

        if (adviceText) {

            adviceText.textContent =
                data.advice;

        }


        /* RESULT CLASS */

        result.className = "result";


        if (data.result === "LIKELY REAL") {

            result.classList.add("likely-real");

        }

        else if (data.result === "LIKELY FAKE") {

            result.classList.add("likely-fake");

        }

        else {

            result.classList.add("uncertain");

        }


        /* SHOW RESULT */

        result.style.display = "block";


        /* SCROLL TO RESULT */

        setTimeout(function () {

            result.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }, 100);


    }

    catch (error) {

        console.error(error);

        alert(
            "Error: " + error.message
        );

    }

    finally {

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


    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

}

/* =========================================================
   SAMPLE NEWS
   ========================================================= */

function loadSample(type) {

    const input = document.getElementById("newsInput");

    if (!input) {
        return;
    }

    if (type === "fake") {

        input.value =
            "Government announces that every citizen will receive free smartphones tomorrow. Share this message with all your contacts immediately to claim your benefit.";

    } else {

        input.value =
            "The government announced a new public initiative today, with officials stating that the programme will be implemented in phases across several regions.";

    }

    // Update word count
    const event = new Event("input", {
        bubbles: true
    });

    input.dispatchEvent(event);

    input.focus();
}

/* =========================================================
   MOBILE NAVIGATION
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const menuToggle = document.getElementById("menuToggle");
    const navLinks = document.getElementById("navLinks");

    if (!menuToggle || !navLinks) {
        return;
    }

    menuToggle.addEventListener("click", function () {

        navLinks.classList.toggle("open");

        if (navLinks.classList.contains("open")) {
            menuToggle.textContent = "×";
            menuToggle.setAttribute("aria-label", "Close menu");
        } else {
            menuToggle.textContent = "☰";
            menuToggle.setAttribute("aria-label", "Open menu");
        }

    });


    // Close menu only when a navigation link is selected
    navLinks.querySelectorAll("a").forEach(function (link) {

        link.addEventListener("click", function () {
            navLinks.classList.remove("open");
            menuToggle.textContent = "☰";
            menuToggle.setAttribute("aria-label", "Open menu");
        });

    });

});