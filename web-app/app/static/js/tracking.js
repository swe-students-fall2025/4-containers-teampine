// =====================================================
// ELEMENTS
// =====================================================
const goLiveBtn = document.getElementById("goLiveBtn");
const liveStatusText = document.getElementById("liveStatusText");
const cameraWrapper = document.getElementById("cameraWrapper");
const video = document.getElementById("camera");
const overlay = document.getElementById("overlay");
const ctx = overlay.getContext("2d");

const spineEl = document.getElementById("spine");
const postureHalo = document.getElementById("postureHalo");
const statusScore = document.getElementById("statusScore");
const sliderStateText = document.getElementById("sliderStateText");

const streakValue = document.getElementById("streakValue");
const goodMinutes = document.getElementById("goodMinutes");
const timelineIndicator = document.getElementById("timelineIndicator");
const statusDot = document.querySelector(".status-dot");

let liveMode = false;
let mlInterval = null;
let scoreHistory = [];


// =====================================================
// STATUS BAR
// =====================================================
function updateLiveStatus(isLive) {
    if (isLive) {
        statusDot.style.background = "#2d8a55";
        statusDot.style.animation = "livePulse 1.8s infinite";
        liveStatusText.textContent = "Live Mode Active";
    } else {
        statusDot.style.background = "#aaa";
        statusDot.style.animation = "none";
        liveStatusText.textContent = "Tracking posture";
    }
}

function updateScore(score) {
    statusScore.textContent = score;
}


// =====================================================
// CAMERA
// =====================================================
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;

        await video.play();

        overlay.width = video.videoWidth;
        overlay.height = video.videoHeight;

    } catch (err) {
        console.error("Camera error:", err);
        alert("Camera access failed");
    }
}


// =====================================================
// SEND FRAME TO ML API
// =====================================================
async function sendFrameToML() {
    // DO NOT USE readyState — it is buggy
    if (!video || video.videoWidth === 0) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const c = canvas.getContext("2d");
    c.drawImage(video, 0, 0);

    const blob = await new Promise(res => canvas.toBlob(res, "image/jpeg"));
    const formData = new FormData();
    formData.append("frame", blob, "frame.jpg");

    try {
        const response = await fetch("/process", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        updateFromML(data);

    } catch (err) {
        console.error("ML ERROR:", err);
    }
}


// =====================================================
// ML → UI
// =====================================================
function updateFromML(result) {
    console.log("ML RESULT:", result);

    if (!result) return;

    const state = result.state || "unknown";
    const score = result.score ?? 0;

    scoreHistory.push(score);
    updateScore(score);

    const postureSlider = document.getElementById("postureSlider");

    // =====================================================
    // HALO + STATE LABEL
    // =====================================================
    if (state === "aligned") {
        sliderStateText.textContent = "Aligned";
        postureHalo.style.borderColor = "rgba(78, 211, 139, 0.4)";
        postureHalo.style.boxShadow = "0 0 20px rgba(78, 211, 139, 0.4)";
    }
    else if (state === "slouch") {
        sliderStateText.textContent = "Slouching";
        postureHalo.style.borderColor = "rgba(255, 106, 106, 0.6)";
        postureHalo.style.boxShadow = "0 0 20px rgba(255, 106, 106, 0.5)";
    }
    else if (state === "neutral") {
        sliderStateText.textContent = "Neutral";
        postureHalo.style.borderColor = "rgba(255, 207, 102, 0.4)";
        postureHalo.style.boxShadow = "0 0 20px rgba(255, 207, 102, 0.4)";
    }
    else {
        sliderStateText.textContent = "No body detected";
        postureHalo.style.borderColor = "rgba(180, 180, 180, 0.4)";
        postureHalo.style.boxShadow = "0 0 20px rgba(180, 180, 180, 0.3)";
    }

    // =====================================================
    // SLIDER (SMOOTH SCORE-BASED MOVEMENT)
    // =====================================================
    let sliderValue = (score - 50) / 50;   // map 0–100 → -1 to 1
    sliderValue = Math.max(-1, Math.min(1, sliderValue)); // clamp
    postureSlider.value = sliderValue;

    // =====================================================
    // SPINE TILT
    // =====================================================
    const tilt = (50 - score) / 5;
    spineEl.style.transform = `translateX(-50%) rotate(${tilt}deg)`;

    // =====================================================
    // TIMELINE
    // =====================================================
    timelineIndicator.style.left = `${score}%`;

    // =====================================================
    // STATS
    // =====================================================
    goodMinutes.textContent = score;
}




// =====================================================
// LIVE MODE TOGGLE
// =====================================================
goLiveBtn.addEventListener("click", async () => {
    liveMode = !liveMode;

    if (liveMode) {
        updateLiveStatus(true);
        goLiveBtn.textContent = "Stop Live";
        cameraWrapper.classList.remove("hidden");

        scoreHistory = [];

        await startCamera();

        // give camera 800ms to warm up
        setTimeout(() => {
            mlInterval = setInterval(sendFrameToML, 350);
        }, 800);

    } else {
        updateLiveStatus(false);
        goLiveBtn.textContent = "Go Live";
        cameraWrapper.classList.add("hidden");

        if (mlInterval) clearInterval(mlInterval);

        // Stop video stream
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
        }

        // Redirect to dashboard to see updated data
        if (scoreHistory.length > 0) {
            window.location.href = "/dashboard";
        }
    }
});
