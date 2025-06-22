FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential gcc libglib2.0-0 libsm6 libxext6 libxrender-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Download NLTK VADER lexicon
RUN python -m nltk.downloader vader_lexicon

# Copy the rest of the code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Streamlit config (optional)
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Run the app (change to your entrypoint if needed)
CMD ["streamlit", "run", "FinSight-Agents/test_main.py", "--server.port=8501", "--server.address=0.0.0.0"]