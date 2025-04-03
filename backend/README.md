# News Ontology Backend

This directory contains the backend API for the News Ontology project, built using Python and FastAPI.

## Prerequisites

*   Python 3.8 or higher

## Dependency Management

This project supports two methods for managing dependencies: Poetry and `requirements.txt`. Choose one method and follow the corresponding instructions.

### Method 1: Poetry (Recommended)

[Poetry](https://python-poetry.org/) is a modern dependency management and packaging tool for Python. It simplifies dependency management, virtual environment handling, and project packaging.

#### Installation

1.  If you don't have Poetry installed, install it following the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).

#### Setup

1.  Navigate to the `backend` directory:

    ```bash
    cd backend
    ```

2.  Install the project dependencies:

    ```bash
    poetry install --no-root
    ```

    The `--no-root` flag tells Poetry to only install the project's dependencies and not try to install the project itself as a package.

3.  Activate the Poetry virtual environment:

    ```bash
    poetry shell
    ```

#### Running the Application

1.  Start the FastAPI application using uvicorn:

    ```bash
    uvicorn app.main:app --reload
    ```

    *   `app.main` refers to the `main.py` file inside the `app` directory.
    *   `app` refers to the FastAPI instance created in `main.py`.
    *   `--reload` enables automatic reloading of the server when you change the code.

### Method 2: `requirements.txt`

This method uses a `requirements.txt` file to specify the project dependencies, managed using `pip`.

#### Setup

1.  Navigate to the `backend` directory:

    ```bash
    cd backend
    ```

2.  Create a virtual environment (optional but highly recommended):

    ```bash
    python -m venv venv
    ```

3.  Activate the virtual environment:

    *   **On Windows:**

        ```bash
        venv\Scripts\activate
        ```

    *   **On macOS/Linux:**

        ```bash
        source venv/bin/activate
        ```

4.  Install the project dependencies from `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

#### Running the Application

1.  Start the FastAPI application using uvicorn:

    ```bash
    uvicorn app.main:app --reload
    ```

## API Endpoints

The backend provides the following API endpoints:

*   `GET /`: Root endpoint, returns a simple "Hello, world" message.
*   `POST /news/`: Receives news data (currently just a text string) and prints it to the console. This endpoint will be extended in future versions to process the news data and interact with the ontology.

## Testing the API

You can test the API endpoints using `curl`, `httpie`, or the Python `requests` library.

**Example using `curl`:**

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text": "This is a test news message from curl!"}' http://localhost:8000/news/