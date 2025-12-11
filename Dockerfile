FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server/ ./server/

# Copy client files
COPY client/ ./client/

# Set environment variables
ENV STATIC_DIR=../client
ENV FLASK_APP=server/server.py
ENV FLASK_ENV=production

EXPOSE 4242

WORKDIR /app/server

CMD ["python", "server.py"]

