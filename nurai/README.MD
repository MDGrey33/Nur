### Local Setup

Run app locally --> `uvicorn app.main:app --reload`

Start the database --> `docker-composer up -d`

PYTHONPATH=../ alembic revision --autogenerate -m "Initialize the db"

PYTHONPATH=../ alembic upgrade head

### Access mysql 
mysql -h127.0.0.1 -P3306 -uuser -ppassword


