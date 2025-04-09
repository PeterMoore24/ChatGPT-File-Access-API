# ChatGPT-File-Access-API
A Python API and OpenAPI schema to connect a custom ChatGPT to a directory on your computer.

# Usage
1) Install the needed dependencies: `pip install fastapi uvicorn pyngrok`
2) Create an API token and set the appropriate environment variable (API_TOKEN).
3) Edit the Python API file and set DIRECTORY_TO_SERVE to the desired directory.
4) Run the Python API file, and copy the output URL.
5) Paste that URL into the OpenAPI file, then paste the contents of that file into your custom GPT's schema.
6) Profit!
