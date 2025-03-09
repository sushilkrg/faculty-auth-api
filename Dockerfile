# Use official Python image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory in container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install system dependencies for dlib and face-recognition
RUN apt-get update && apt-get install -y \
    cmake \
    libgtk2.0-dev \
    pkg-config \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    python3-pip \
    python3-dev \
    python3-setuptools \
    && apt-get clean

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start the Django application
CMD ["gunicorn", "faculty-auth-api.wsgi:application", "--bind", "0.0.0.0:8000"]
