# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Start of Selection
# Copy the pyproject.toml, poetry.lock files, and README.md
COPY pyproject.toml poetry.lock* README.md /app/

RUN pip config set global.trusted-host \
    "pypi.org files.pythonhosted.org pypi.python.org" \
    --trusted-host=pypi.python.org \
    --trusted-host=pypi.org \
    --trusted-host=files.pythonhosted.org

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry source add fpho https://files.pythonhosted.org
RUN poetry config certificates.fpho.cert false
RUN poetry source add pypi
RUN poetry config certificates.PyPI.cert false
RUN poetry config certificates.pypi.cert false
RUN poetry install

# Copy the rest of the application code
COPY . /app

# Command to run the application
CMD ["poetry", "run", "python", "main.py"]
