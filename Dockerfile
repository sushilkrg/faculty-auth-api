# Use lightweight Python image
FROM python:3.11-slim

# Set environment variables to reduce buffer and maximize memory
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies required for face recognition
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    python3-dev \
    libboost-all-dev \
    build-essential \
    cmake

# Create a directory for the app
WORKDIR /app

# Install Python dependencies from requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

# ✅ Copy the prebuilt dlib wheel from your project folder to the Docker container
COPY wheels/dlib-19.24.6-cp311-cp311-linux_x86_64.whl ./wheels/

# ✅ Install the pre-built dlib wheel (NO COMPILATION)
RUN pip install ./wheels/dlib-19.24.6-cp311-cp311-linux_x86_64.whl

# ✅ Copy all project files into the container
COPY . .

# ✅ Collect static files (important in Render)
RUN python manage.py collectstatic --noinput

# ✅ Expose the port Render will use
EXPOSE 8000

# ✅ Command to run the app
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
