# Darukaa.Earth

Geospatial data analytics platform for managing and visualizing carbon and biodiversity projects. 

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy (Async), Alembic, Pydantic, PostgreSQL + PostGIS
- **Frontend**: React, Vite, TypeScript, Mapbox GL JS, Chart.js

---

## How to Run the Project Locally

Follow these steps to run the full application (Database, Backend, and Frontend) on your local machine.

### 1. Start the Database (PostgreSQL + PostGIS)

The backend requires a PostGIS-enabled PostgreSQL database for geospatial operations. You can run one easily using Docker.

Run this command in your terminal:
```bash
docker run -d \
  --name darukaa-postgis \
  -e POSTGRES_USER=darukaa \
  -e POSTGRES_PASSWORD=darukaa_password \
  -e POSTGRES_DB=darukaa_db \
  -p 5432:5432 \
  postgis/postgis:15-3.3
```
*(If you already have a Postgres server running locally on port 5432, you'll need to stop it or change the mapping, e.g., `-p 5433:5432`, and update the `DATABASE_URL` in your backend `.env` accordingly).*

### 2. Run the Backend (FastAPI)

Open a new terminal and navigate to the backend directory:

```bash
cd backend
```

**Set up a virtual environment and install dependencies:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Set environment variables:**
Create a `.env` file in the `backend/` folder:
```bash
cp .env.example .env
```
Ensure the `.env` has the correct `DATABASE_URL`:
`DATABASE_URL=postgresql+asyncpg://darukaa:darukaa_password@localhost:5432/darukaa_db`

**Run database migrations (create tables):**
```bash
alembic upgrade head
```

**Start the FastAPI server:**
```bash
uvicorn app.main:app --reload
```
*The backend is now running at: http://localhost:8000*
*You can view the interactive API docs at: http://localhost:8000/docs*

### 3. Run the Frontend (React + Vite)

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```

**Install dependencies:**
```bash
npm install
```

**Set environment variables:**
Create a `.env` file in the `frontend/` folder:
```bash
cp .env.example .env
```
Open `.env` and add your Mapbox token (needed for the maps to render):
```env
VITE_API_URL=http://localhost:8000/api
VITE_MAPBOX_TOKEN=pk.your_actual_mapbox_token_here
```

**Start the Vite development server:**
```bash
npm run dev
```
*The frontend is now running at: http://localhost:5173*

---

## Usage

1. Open http://localhost:5173 in your browser.
2. Click **Create one** to register a new account.
3. Once logged in, you can create a Project.
4. Open the Project to draw Site polygons on the map and view mock analytics!
