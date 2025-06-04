# 🎙️ myAiFrontDesk – Real-Time Voice Assistant 

# Demo

[![Watch the video](https://img.youtube.com/vi/lg8gasm7ReY/0.jpg)](https://www.youtube.com/watch?v=lg8gasm7ReY)

This is  **project** built to simulate a real-time voice assistant using Gemini, Django, WebSockets, and a lightweight in-house knowledge base.
### 🔐 Environment Variables

Create a `.env` file in your ./saloon/agents with the following keys:

```env
# Cartesia TTS Service
CARTESIA_API_KEY=

# LiveKit Realtime Communication
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
LIVEKIT_URL=

# Gemini or Google API
GOOGLE_API_KEY=
---
```



## ⚙️ Setup Instructions

### 1. Activate Python Environment

```bash
source myenv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🧠 Run the AI Agent

From the root directory:

```bash
python saloon/agent/main.py
```

This launches the AI assistant logic that connects via WebSocket to the Django backend.

---

## 🛠️ Run the Django Backend

Use Daphne to serve ASGI (WebSocket + HTTP):

```bash
daphne -p 8000 djangoBackend.asgi:application
```

Make sure to run migrations first if needed:

```bash
python manage.py migrate
```

---

## 🌐 Open the Frontend

Open the main HTML UI (update path if needed):

```bash
open ws_test.HTML
```

Or open it in any browser manually.

---

##  Model Selection & Livekit

We started by **LiveKit model installation**. We chose multiple LLMs before ending up on the **Realtime model provided by Gemini**, which suited our case.  

Other methods were also explored like **STT → LLM → TTS** pipeline but it was not as fast as required for this specific case.  
Also, this would cause multiple **SaaS subscriptions**, contributing to financial overhead.  

Still, for **query resolve requirements**, we use **TTS provided by Catesia**.  
Gemini has built-in STT, hence we are not required to deal with it at this stage.  

For using **in-house models and services** such as **Ollama**, we would be required to deal with the full **STT → LLM → TTS** pipeline.

---

## 🧰 Backend Design

Now, primarily we use **Django as a backend service**. This gives us access to the full Django ecosystem including Django Admin.  

For communication, we use **WebSocket** for the to-and-fro of data during conversation—  
e.g., if the customer has a query which is resolved during the call.

For **knowledge storage**, regular **REST API** could do the work—like after ending the conversation, storing important points in the database that might serve as a **KnowledgeBase** of the Agent.

---

## 🗃️ Database Design Approach

There are currently three models/tables we are concerned with:

### 1. Customer
- This includes customer details such as **name**, **phone**, etc.
- Unique constraints could be used to uniquely identify the customer during the call using number and name.

### 2. Query
- Stores the questions that LLM could not solve.
- Fields: `query question`, `was_resolved`, `answer to query`, `expiry time`.
- This model works with **WebSocket** to provide **real-time query solving** capability.
- If the query is not solved within a certain period of time, the query remains **unresolved**.

### 3. KnowledgeBase
- As soon as the query is solved, it is stored in this table.
- Before initializing any agent session, the knowledge table is fetched and **fed to the model** so that it can answer already solved general queries.

---

## 🗂️ Project Structure

```
AIFRONT/
├── appointmentHandler/              # Django app for appointment handling
├── djangoBackend/                   # Project-level configs (settings, ASGI, etc.)
├── myenv/                           # Python virtual environment
├── saloon/                          # Main salon assistant backend
│   ├── admin.py                     # Admin interface
│   ├── consumer.py                  # WebSocket consumer
│   ├── models.py                    # Models: Customer, Query, KnowledgeBase
│   ├── routing.py                   # WebSocket routing
│   ├── serializers.py               # API serialization
│   ├── signals.py                   # Auto logic on model save
│   ├── urls.py                      # API endpoints
│   ├── views.py                     # API logic
│   ├── templates/                   # HTML templates
│   └── agent/                       # Core AI Assistant logic
│       ├── greeter_model/           # Greeter-specific logic
│       │   └── models.py
│       ├── .env                     # Local env for agent module
│       ├── agent.py                 # Base agent class
│       ├── api.py                   # API utilities
│       ├── config.py                # Agent settings
│       ├── main.py                  # Entrypoint
│       ├── models.py                # Internal models
│       ├── prompts.py               # Prompt templates
│       ├── salon_agent.log
│       ├── tools.py                 # Helper functions
│       └── webSocketConnection.py   # WebSocket link to Django
├── .env                             # Global env vars
├── db.sqlite3                       # SQLite DB for local
├── manage.py                        # Django manager
└── requirements.txt                 # Dependencies
```


---

## ✅ Project Covers the following

- Every question or query that model sends for human intervention has a **lifecycle**:
  - Initial State: `Pending`
  - After a timeout: `Unresolved`
  - If resolved by supervisor: marked as `Resolved`
  
- Clear link between the **question unresolved** and **agent calling back** to customer  
- **Immediately once supervisor responds**, it is:
  - Stored in DB
  - Used to **train/improve model** for future sessions

- Very **basic page** where **pending requests are shown via WebSocket in realtime**

---


