# Use a Python base image with some pre-installed dependencies
FROM python:3.9-slim

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only the backend since we have the static frontend inside it
COPY backend/ ./

# Create and set permissions for the database
RUN mkdir -p /app/database && chmod 777 /app/database

# Install dependencies
# We use a custom flag to try and stay within memory limits
RUN pip install --no-cache-dir flask flask-cors opencv-python-headless numpy

# Note: DeepFace is excluded here to ensure the build succeeds on Render Free Tier.
# If you upgrade to a paid plan with more RAM, uncomment the line below.
# RUN pip install --no-cache-dir deepface tf-keras tensorflow

EXPOSE 5000

CMD ["python", "app.py"]
