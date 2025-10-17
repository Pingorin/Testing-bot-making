# Dockerfile

# Use Python 3.10.8 runtime as a parent image
FROM python:3.10.8-slim  # <--- Version updated here

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the dependency file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the container
COPY . .

# Expose the port the app runs on (used by Render)
ENV PORT=8080

# Dockerfile

# ... (Installation steps)

# Run the bot when the container starts using the explicit python3 command
CMD ["python3", "bot.py"]
