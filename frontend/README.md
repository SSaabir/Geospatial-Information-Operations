Perfect 👌 let’s write down **clear step-by-step instructions** so that a new collaborator can:

1. Clone the repo
2. Configure the **React frontend**
3. Configure the **FastAPI backend (.venv + requirements.txt)**
4. Run everything locally

---

# 🛠️ Setup Guide (Frontend + Backend)

## 1. Clone the Repository

---

## 2. Backend Setup (FastAPI + .venv)

### Create & Activate Virtual Environment

```bash
cd services
python -m venv .venv
```

Activate the venv:

* **Windows (PowerShell):**

  ```bash
  .venv\Scripts\activate
  ```
* **Mac/Linux:**

  ```bash
  source .venv/bin/activate
  ```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Run Backend Server

```bash
uvicorn main:app --reload
```

➡ Server will run on [http://localhost:8000](http://localhost:8000)

---

## 3. Frontend Setup (React + Vite)

### Install Node Modules

```bash
cd ../frontend
npm install
```

### Run Frontend Server

```bash
npm run dev
```

➡ Frontend will run on [http://localhost:5173](http://localhost:5173)
