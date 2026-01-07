Immersive AI-Powered Education Platform

EduTech VR is a next-generation learning platform that blends Artificial Intelligence with Virtual Reality to make education more interactive, visual, and engaging. Instead of just reading or watching, learners can step inside simulations, collaborate in virtual classrooms, and interact with AI that truly understands their study material.

Whether you’re exploring physics experiments, chatting with your own notes, or collaborating in a VR classroom — EduTech VR turns learning into an experience.

-> What Makes EduTech VR Special?
-> AI Study Assistant

Upload your PDFs and study notes, then chat with them like a tutor. Powered by a Retrieval-Augmented Generation (RAG) system, the assistant gives accurate, context-aware answers straight from your materials.

-> Natural Language → Interactive Experiments

Describe what you want in plain English, and EduTech VR generates interactive 3D simulations for you:

“Show a simulation of flocking birds”

“Create a network packet routing demo”

No coding required — just imagination.

-> Immersive VR Classrooms

Learn and collaborate in shared virtual spaces. Attend classes, discuss concepts, and work together in real time — all inside VR.

-> Hands-On VR Experiments

Dive into pre-built 3D experiments across physics, chemistry, and biology, designed to make abstract concepts intuitive and memorable.

-> Tech Stack
Frontend

Framework: Next.js 15 (App Router)

UI: React 19, Radix UI, Shadcn UI

Styling: Tailwind CSS 4

3D / VR: Three.js, React Three Fiber, React Three XR

Charts & Visualization: Recharts

Backend

Framework: FastAPI (Python)

AI / LLM: Ollama (Local inference)

mistral – Chat & RAG

qwen2.5-coder:7b – Code generation

Vector Database: FAISS

PDF Processing: Docling (OCR + deep document search)

-> Prerequisites

Before getting started, make sure you have:

Node.js (v18 or higher)

Python (v3.10 or higher)

Ollama installed
-> https://ollama.ai/

Pull the required models:

ollama pull mistral
ollama pull qwen2.5-coder:7b

-> Installation & Setup
-> Frontend Setup

From the project root:

# Install dependencies
npm install

# Start development server
npm run dev


The frontend will be available at:
-> http://localhost:3000

-> Backend Setup

The backend is split into two FastAPI services:

Experiment Generator → main_ce.py

PDF Chat / RAG Service → main_cn.py

Navigate to the backend folder:

cd backend

# (Optional but recommended) Create virtual environment
python -m venv venv

# Activate it
# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

-> Running Backend Services

Run each service on a different port.

Experiment Generator

uvicorn main_ce:app --reload --port 8000


PDF Chat / RAG Service

uvicorn main_cn:app --reload --port 8001


-> If you change ports, make sure the frontend API endpoints match.

-> Project Structure
.
├── app/                   # Next.js frontend
│   ├── api/               # API routes
│   ├── classroom/         # VR classrooms
│   ├── experiments/       # Interactive VR experiments
│   ├── dashboard/         # User dashboard
│   
├── backend/               # FastAPI backend
│   ├── create_experiment/ # LLM experiment generation logic
│   ├── chat_with_notes/   # PDF RAG pipeline
│   ├── data/              # Vector database files
│   ├── uploads/           # Uploaded PDFs
│   ├── main_ce.py         # Experiment Generator entry point
│   └── main_cn.py         # PDF Chat entry point


-> Contributing

Contributions are welcome and appreciated!

Fork the repository

Create a new branch

git checkout -b feature/your-feature-name


Commit your changes

git commit -m "Add awesome feature"


Push to your fork

git push origin feature/your-feature-name


Open a Pull Request 

 License

This project is licensed under the MIT License — feel free to use, modify, and build upon it.
