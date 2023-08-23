# Authorisation service

## Database migrations
Generate migrations
```
alembic revision --autogenerate -m "Added account table"
```

Apply migrations
```
alembic upgrade head
```

Reset DB to zero
```
alembic downgrade base
```
