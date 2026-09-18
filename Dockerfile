FROM python:3.10-slim

# Create a non-root user
RUN useradd -m -u 1000 user
USER user

# Add user's local Python binaries to PATH
ENV PATH="/home/user/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Install backend dependencies
COPY --chown=user backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the entire project
COPY --chown=user . .

# Render provides the PORT environment variable
EXPOSE 10000

# Start the FastAPI server
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]