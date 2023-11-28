# Media Manager

## Prerequisites

- Python 3.12.0

## How it works?

The Flask API, when triggered, will perform an operation based on the "req_type" received in the POST request.

## Run Locally

1. Clone this repository.

2. Create a virtual environment inside the `api` folder and install requirements.

```bash
python -m venv .venv
```

3. Activate the created `.venv` environment.

```bash
source .venv/Scripts/activate
```

4. In the `api` folder, install the necessary dependencies.

```bash
pip install -r requirements.txt
```

5. Go to the `api\media_manager` folder and start the API server locally.

```bash
python __init__.py
```

## POST request

Copy your media files into the `input` folder and make a POST request to the API using the following body.

```http
{
    "req_type": "organize_media_folder"
}
```