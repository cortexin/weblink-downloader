### To run in docker-compose

- `cp .env.example .env`
- `docker-compose up -d`
-  The service will be available at `localhost:8000`

### To run tests
- `pipenv shell`
- `pipenv install --dev`
- `py.test`
