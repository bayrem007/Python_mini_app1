# Pur Beurre - Healthy Food Substitution

Full-stack app to search **healthier substitutes** for food products using the **OpenFoodFacts** API.

## Tech stack

- **Backend**: Django + Django REST Framework
- **Frontend**: React (Vite)
- **Database**: MongoDB Atlas (MongoEngine for domain data)
- **External data**: OpenFoodFacts API

## Repository layout (initial architecture)

```
backend/                  # Django project (HTTP boundary + app modules)
  purbeurre/              # Django project settings + root URLs
  api/                    # API layer (DRF views + routing)
  users/                  # User-related domain (Django auth/profile)
  products/               # Product domain (MongoEngine Documents + services)
  substitutions/          # Substitution domain (services + favorites)
  data_loader/            # OpenFoodFacts client + import services
  requirements.txt

frontend/                 # React app
  src/
    components/           # UI building blocks (presentational)
    pages/                # Route-level screens (composition)
    services/             # HTTP client(s) / data access from UI
    hooks/                # Reusable UI hooks (querying, state)
```

## Clean architecture mapping (what goes where)

- **API layer (HTTP boundary)**: `backend/api/`
  - `views.py`: DRF endpoints (thin controllers) that validate input and call app/domain services.
  - `urls.py`: routes under `/api/*`.
  - `serializers.py`: request/response shapes (DTOs).

- **Business logic layer (use cases / domain services)**:
  - `backend/products/services.py`: search + “healthier substitute” selection rules.
  - `backend/substitutions/services.py`: substitution use-cases (find, save favorites).
  - `backend/data_loader/services.py`: ingestion use-cases (fetch + upsert).

- **Data access layer**:
  - `backend/products/models.py`: MongoEngine `Document` definitions (`Product`, `Category`).
  - `backend/substitutions/models.py`: MongoEngine `Document` definitions (`Substitution`, `FavoriteSubstitution`).
  - `backend/purbeurre/mongo.py`: MongoEngine connection bootstrap.

## Environment configuration

- Copy `.env.example` to `.env` and fill `MONGODB_URI` for MongoDB Atlas.
- Frontend: copy `frontend/.env.example` to `frontend/.env` to set `VITE_API_BASE_URL`.

## Run (dev)

Backend:

```bash
cd backend
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

