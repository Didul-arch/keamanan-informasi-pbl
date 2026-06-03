# 1. Use a minimal Python image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /src

# 3. Copy dependencies and install them
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Buat direktori storage
RUN mkdir -p storage

# (Opsional) Pastikan hak aksesnya bisa ditulis 
RUN chmod 777 storage
    
# 4. Copy application code — all three packages
COPY ./backend ./backend
COPY ./database ./database
COPY ./digital_signature ./digital_signature

# Copy Alembic config (now run from project root)
COPY ./backend/alembic.ini ./backend/alembic.ini

# 5. Command to run the app using Uvicorn (from project root)
CMD alembic -c backend/alembic.ini upgrade head && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
