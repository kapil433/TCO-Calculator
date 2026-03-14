# Get TCO Calculator running on localhost

You need **two terminals**: one for the backend, one for the frontend. Do **not** open `index.html` in the browser by double-clicking — it will not work.

---

## Step 1: Backend (Terminal 1)

Open PowerShell or Command Prompt and run:

```powershell
cd C:\Users\Kapil\TCO-Calculator\backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Leave this running. You should see:

```
Uvicorn running on http://0.0.0.0:8000
```

- **API:** http://localhost:8000  
- **Swagger docs:** http://localhost:8000/docs  

If you see "No module named 'app'", run from the `backend` folder (the one that contains the `app` folder).

---

## Step 2: Frontend (Terminal 2)

Open a **second** terminal and run:

```powershell
cd C:\Users\Kapil\TCO-Calculator\frontend
npm run dev
```

Leave this running. You should see something like:

```
  VITE v5.x.x  ready in xxx ms
  ➜  Local:   http://localhost:5173/
```

- **App (UI):** open **http://localhost:5173** in your browser.

---

## Step 3: Use the app

1. In the browser go to **http://localhost:5173** (not file:// and not port 8000).
2. Select state, years, ex-showroom price and click **Calculate TCO**.

---

## If the page is blank

- Make sure you opened **http://localhost:5173** (frontend), not only the backend.
- Make sure **both** backend and frontend are running (both terminals).
- If the State dropdown has only 3 options and an orange message, the backend is not reachable — start the backend (Step 1) and refresh the page.

## If you never created the virtualenv

In the **backend** folder, run once:

```powershell
cd C:\Users\Kapil\TCO-Calculator\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Then run the uvicorn command from Step 1.
