# Use Python 3.8 image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container at /app
COPY . /app

# Install any dependencies
RUN pip install -r requirements.txt

# Command to run on container start
CMD ["python", "main.py"]
