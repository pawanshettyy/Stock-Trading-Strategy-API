FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Prisma client
RUN pip install prisma

# Copy the rest of the application
COPY backend/ .

# Generate Prisma client
RUN npx prisma generate

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]