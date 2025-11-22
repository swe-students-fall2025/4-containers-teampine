# 📌 SitStraight: AI-Powered Posture Monitoring System

![ML Client CI](https://github.com/USER/REPO/actions/workflows/ml-client-ci.yml/badge.svg)
![Web App CI](https://github.com/USER/REPO/actions/workflows/web-app-ci.yml/badge.svg)

> **SitStraight** is an intelligent, containerized posture monitoring system that helps users build healthier sitting habits through real-time AI analysis and intuitive data visualization.

---

## 👥 Team Members

- [Team Member 1](https://github.com/username1)
- [Team Member 2](https://github.com/username2)
- [Team Member 3](https://github.com/username3)
- [Team Member 4](https://github.com/username4)

---

## 🎯 Problem Statement

Modern life forces most people — students, remote workers, gamers — to sit in front of screens for hours at a time. Over time, this leads to:

- Chronic back and neck pain  
- Spinal misalignment  
- Reduced energy and productivity  
- Poor long-term posture habits  

Most people **do not realize they're slowly developing poor posture until it's too late**.

---

## 💡 Our Solution

**SitStraight** uses machine learning to analyze sitting posture in real time, detect poor posture patterns, and provide actionable insights through a web dashboard.

### Key Features:
- 🤖 **AI-Powered Analysis** - Uses MediaPipe Pose for real-time posture detection
- 📊 **Visual Dashboard** - Track posture scores, slouch time, and improvement trends
- 🔒 **Privacy First** - All processing happens locally, no video stored
- 🐳 **Fully Containerized** - Easy deployment with Docker Compose

---

## 🏗️ System Architecture

SitStraight consists of **three containerized subsystems**:

```
┌─────────────────────────────────────────────────────────────┐
│                     SitStraight System                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐      ┌──────────────────┐             │
│  │   Web Browser   │─────▶│   Flask Web App  │             │
│  │  (port 5000)    │      │   (container)    │             │
│  └─────────────────┘      └──────────────────┘             │
│           │                        │                        │
│           │ sends frames           │ stores/reads           │
│           │                        │                        │
│           ▼                        ▼                        │
│  ┌─────────────────┐      ┌──────────────────┐             │
│  │   ML Client     │◀────▶│     MongoDB      │             │
│  │  (port 5002)    │      │  (port 27017)    │             │
│  └─────────────────┘      └──────────────────┘             │
│   Posture Analysis         Data Storage                     │
└─────────────────────────────────────────────────────────────┘
```

### Container 1: Machine Learning Client (`machine-learning-client/`)

**Purpose:** Analyzes posture using MediaPipe Pose and stores results in MongoDB.

- **Technology:** Python, Flask, MediaPipe, OpenCV, PyMongo
- **Port:** 5002
- **Functionality:**
  - Receives video frames via REST API
  - Performs real-time posture analysis
  - Calculates posture scores (0-100)
  - Classifies posture as "aligned", "neutral", or "slouch"
  - Stores analysis results in MongoDB

### Container 2: Web Application (`web-app/`)

**Purpose:** User interface for authentication, posture tracking, and data visualization.

- **Technology:** Python, Flask, PyMongo, Jinja2
- **Port:** 5000
- **Functionality:**
  - User registration and authentication
  - Dashboard with posture metrics
  - Weekly/monthly trend visualization
  - Browser-based webcam capture
  - Communicates with ML client for analysis

### Container 3: MongoDB Database

**Purpose:** Persistent data storage for users and posture samples.

- **Technology:** MongoDB 7
- **Port:** 27017
- **Collections:**
  - `users` - User accounts and credentials
  - `posture_samples` - Timestamped posture analysis results

---

## 🚀 Getting Started

### Prerequisites

Before running SitStraight, ensure you have:

- **Docker Desktop** installed and running
  - [Download for Windows/Mac](https://www.docker.com/products/docker-desktop/)
  - [Install on Linux](https://docs.docker.com/engine/install/)
- **Git** (to clone the repository)
- **Webcam** (for posture detection)

### Quick Start (3 Steps)

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/sitstraight.git
cd sitstraight
```

#### 2. Start All Containers

##### windows
```bash
docker-compose up --build
```

##### Mac os
```bash
docker compose up --build
```

This single command will:
- ✅ Start MongoDB database
- ✅ Build and start the ML client
- ✅ Build and start the web app

**First-time setup takes 2-3 minutes** to download dependencies.

#### 3. Access the Application

Open your browser and navigate to:

```
http://localhost:5000
```

**Create an account:**
- Click "Register"
- Enter your name, email, and password
- Password must have: 6+ characters, 1 uppercase, 1 lowercase, 1 number

**Start tracking:**
- Log in and go to "Dashboard"
- Click "Start Tracking" to begin monitoring your posture

---

## ⚙️ Configuration

### Environment Variables

The system uses the following environment variables (configured in `docker-compose.yml`):

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGO_URI` | `mongodb://mongodb:27017/sitstraight` | MongoDB connection string |
| `FLASK_SECRET_KEY` | `dev_secret_change_in_production` | Flask session secret |
| `ML_CLIENT_URL` | `http://ml-client:5002` | ML client service URL |

### Creating a Custom Configuration

If you need to customize settings:

1. Copy the example environment file:
```bash
cp env.example .env
```

2. Edit `.env` with your values:
```bash
MONGO_URI=mongodb://mongodb:27017/sitstraight
FLASK_SECRET_KEY=your_secure_secret_key_here
```

3. Update `docker-compose.yml` to use the `.env` file.

---

## 🧪 Development

### Running Tests

Both subsystems include unit tests with pytest.

**Test ML Client:**
```bash
cd machine-learning-client
pip install -r requirements.txt
pytest tests/ --cov=src --cov-report=term-missing
```

**Test Web App:**
```bash
cd web-app
pip install -r requirements.txt
pytest tests/ --cov=app --cov-report=term-missing
```

### Code Formatting and Linting

**Format code with Black:**
```bash
# ML Client
cd machine-learning-client
black src/

# Web App
cd web-app
black app/
```

**Lint with Pylint:**
```bash
# ML Client
cd machine-learning-client
pylint src/

# Web App
cd web-app
pylint app/
```

### Continuous Integration

The project includes GitHub Actions workflows that automatically:
- ✅ Run linting (Black, Pylint)
- ✅ Execute unit tests
- ✅ Check code coverage (target: 80%)

Workflows run on every push and pull request to `main`.

---

## 🛠️ Running Individual Containers

If you prefer to run containers separately for development:

### 1. Start MongoDB

```bash
docker run -d --name mongodb -p 27017:27017 mongo:7
```

### 2. Start ML Client

```bash
cd machine-learning-client
docker build -t ml-client .
docker run -p 5002:5002 --link mongodb -e MONGO_URI=mongodb://mongodb:27017 ml-client
```

### 3. Start Web App

```bash
cd web-app
docker build -t web-app .
docker run -p 5000:5000 --link mongodb --link ml-client \
  -e MONGO_URI=mongodb://mongodb:27017 \
  -e ML_CLIENT_URL=http://ml-client:5002 \
  web-app
```

---

## 🪟 Windows Camera Access Note

**Important:** Docker on Windows has limited direct webcam access from containers.

### Solution: Browser-Based Capture (Recommended)

The web app uses **browser-based webcam capture**, which works on all platforms:
- Your browser captures frames
- Frames are sent to the ML client for analysis
- Results are stored in MongoDB and displayed on the dashboard

This approach works seamlessly on Windows, Mac, and Linux.

### Alternative: Run ML Client Locally

For continuous background monitoring:

```bash
cd machine-learning-client
pip install -r requirements.txt
python src/main.py  # Runs continuous webcam loop
```

Make sure MongoDB is running via Docker:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:7
```

---

## 🛑 Stopping the Application

Press `Ctrl + C` in the terminal running docker-compose, then:

```bash
docker-compose down
```

**To remove all data (including database):**

```bash
docker-compose down -v
```


## Click link
http://localhost:5000
---

## 📁 Project Structure

```
sitstraight/
├── machine-learning-client/       # ML posture analysis service
│   ├── src/
│   │   ├── app.py                # Flask API for frame processing
│   │   ├── main.py               # Continuous webcam monitoring
│   │   ├── posture_detector.py   # MediaPipe posture analysis
│   │   └── database.py           # MongoDB connection
│   ├── tests/                    # Unit tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── web-app/                      # Flask web dashboard
│   ├── app/
│   │   ├── app.py               # Flask routes
│   │   ├── db.py                # Database models
│   │   ├── templates/           # HTML templates
│   │   └── static/              # CSS, JS assets
│   ├── tests/                   # Unit tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── .github/workflows/           # CI/CD pipelines
│   ├── ml-client-ci.yml
│   ├── web-app-ci.yml
│   └── lint.yml
│
├── docker-compose.yml           # Multi-container orchestration
├── env.example                  # Environment variables template
└── README.md                    # This file
```

---

## 🤝 Contributing

We follow an agile development workflow:

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and commit: `git commit -m "Add feature"`
3. Push to GitHub: `git push origin feature/your-feature`
4. Open a Pull Request
5. Wait for code review and CI checks
6. Merge after approval

**Code must:**
- ✅ Pass all linting checks (Black, Pylint)
- ✅ Include unit tests
- ✅ Maintain 80%+ code coverage

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Useful Links

- [MediaPipe Pose Documentation](https://google.github.io/mediapipe/solutions/pose)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Docker Image](https://hub.docker.com/_/mongo)

---

## 📊 Technology Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python 3.10, Flask
- **ML Framework:** MediaPipe Pose
- **Image Processing:** OpenCV
- **Database:** MongoDB 7
- **Containerization:** Docker, Docker Compose
- **CI/CD:** GitHub Actions
- **Testing:** Pytest
- **Code Quality:** Black, Pylint

---

**Built with ❤️ for better posture and healthier living**
