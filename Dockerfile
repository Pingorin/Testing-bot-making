# Use an official Python runtime as a parent image
FROM python:3.11.5-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the dependency file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the container
COPY . .

# Expose the port the app runs on (used by Render)
# PORT 8080 is often used, but Render will use the one set in the runtime
ENV PORT=8080

# Run the bot when the container starts
CMD ["python", "bot.py"]
