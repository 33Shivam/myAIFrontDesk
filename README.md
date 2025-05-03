# 🎙️ myAiFrontDesk – Real-Time Voice Assistant (Assignment Project)

This is an **assignment project** built to simulate a real-time voice assistant using Gemini, Django, WebSockets, and a lightweight in-house knowledge base.

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

