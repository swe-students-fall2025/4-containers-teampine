# 📌 SitStraight: AI-Powered Posture Monitoring Habit Builder

![ML Client CI](https://github.com/USER/REPO/actions/workflows/ml-client-ci.yml/badge.svg)
![Web App CI](https://github.com/USER/REPO/actions/workflows/web-app-ci.yml/badge.svg)

> **SitStraight** is an intelligent, camera-based posture monitoring system designed to help users build healthier sitting habits.  
> Using lightweight machine learning and an intuitive dashboard, SitStraight detects slouching, leaning, and prolonged sitting — then visualizes posture trends to help users develop long-term ergonomic habits.

---

## Problem

Modern life forces most people — students, remote workers, gamers — to sit in front of screens for hours at a time.  
Over time, this leads to:

- chronic back and neck pain  
- spinal misalignment  
- reduced energy  
- poor long-term posture habits  

Most people **do not realize they’re slowly ruining their posture until it’s too late**.

---

## Our Solution: SitStraight

**SitStraight** is a posture habit-builder that uses your webcam to analyze your sitting posture in real time.

### SitStraight detects:
- Slouching  
- Leaning left or right  
- Sitting too close or too far from the screen  
- Time spent sitting without breaks  

All posture data is recorded in a MongoDB database and displayed on an intuitive web dashboard.

---

##  System Architecture

SitStraight is composed of **three Dockerized subsystems**:



---

## 🤖 Machine Learning Client (Posture Analyzer)

Located in: **`machine-learning-client/`**

### Responsibilities:
- Access webcam frames every few seconds  
- Use **Mediapipe Pose** to detect:
  - spine angle  
  - shoulder alignment  
  - head distance from camera  
- Classify posture as:
  - `good`  
  - `slouch`  
  - `lean_left`  
  - `lean_right`  
  - `too_close` / `too_far`  
- Save metadata to MongoDB, including:
  - timestamp  
  - posture classification  
  - frame-based metrics  
  - ML confidence score  

### Technical Requirements:
- Python  
- Mediapipe  
- PyMongo  
- Docker container  
- PEP 8 formatting (Black)  
- Pylint linting  
- Pytest (80%+ coverage)  
- GitHub Actions CI workflow  

---

## 🌐 Flask Web App Dashboard

Located in: **`web-app/`**

### Features:
- **Posture Score:** daily evaluation of posture quality  
- **Daily Slouch Time:** minutes spent with bad posture  
- **Weekly Improvement Chart:** visual progress graph  
- **Real-Time Alerts:** notification when posture declines  

### Technical Requirements:
- Flask  
- PyMongo  
- Jinja2 templates  
- Docker container  
- Pytest + pytest-flask (80%+ coverage)  
- PEP 8 formatting  
- GitHub Actions CI  

---

## 🛠️ Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/sitstraight.git
cd sitstraight

