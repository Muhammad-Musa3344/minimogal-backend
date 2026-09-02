# Mogul Mind Backend

## Setup

1. Clone this repo
2. Create a virtual environment:
python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # Mac/Linux

3. Install dependencies:

pip install -r requirements.txt

4. Copy `.env.example` to `.env` and fill in real values (ask team lead for keys)
5. Run the schema in Supabase SQL Editor (see `app/db/schema.sql`)
6. Start the server:

uvicorn app.main:app --reload --port 8000

7. Visit `http://localhost:8000/docs` to test endpoints



