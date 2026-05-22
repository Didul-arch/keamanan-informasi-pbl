# 1. Use a minimal Python image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy dependencies and install them
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy your application code
COPY ./backend ./backend
COPY ./database ./database
COPY ./digital_signature ./digital_signature
# Copy Alembic config and migrations so we can run migrations inside the container
COPY ./backend/alembic.ini ./alembic.ini
COPY ./backend/alembic ./alembic

# 5. Command to run the app using Uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
