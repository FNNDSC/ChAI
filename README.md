# ChAI - A Natural Language Assistant Using ChRIS

https://github.com/user-attachments/assets/9a3ea458-5de3-4e42-a68b-f656c8e63365


This repository sets up a local development environment for the ChAI assistant.

It leverages **Ollama** as the model inference backend and **Streamlit** for the user interface.

This guide will walk you through the setup and usage process.

## Prerequisites

Before you begin, ensure you have the following installed and configured:

- **Python 3.11** (or a compatible version)
- **Ollama** installed locally (refer to the [Ollama installation guide](<ollama_installation_link>))
- **Streamlit** installed for the UI (`pip install streamlit`)
- **LlamaStack** installed for managing models and inference (`pip install llama-stack`)

### Install Python and Virtual Environment

1.  **Verify Python Installation:** Ensure Python 3.11 is installed on your system. You can check the version by running:

    ```bash
    python3 --version
    ```

2.  **Create and Activate Virtual Environment:** It's highly recommended to use a virtual environment to manage dependencies.

    ```bash
    python3.11 -m venv .chenv
    source .chenv/bin/activate
    ```

### Install Dependencies

With the virtual environment activated, install the necessary Python packages listed in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

**Note:** If Ollama and LlamaStack Client are not included in your `requirements.txt`, please install them separately following their respective installation instructions.

### Setting Up and Running the Application

1.  **Start Ollama Model (`llama3.2:3b`):**

    Initiate the Ollama model using the `llama-stack` build command:

    ```bash
    INFERENCE_MODEL=llama3.2:3b llama stack build --template ollama --image-type venv --run
    ```

2.  **Activate Virtual Environment (if needed):**

    If you've closed your terminal or deactivated the environment, reactivate it:

    ```bash
    source .chenv/bin/activate
    ```

3.  **Run Streamlit Application:**

    With the virtual environment active, launch the Streamlit application:

    ```bash
    streamlit run app.py
    ```

4.  **Accessing the Application:**

    Once the Streamlit app is running, you will see output similar to:

    ```
    Local URL: http://localhost:8501
    Network URL: http://<your-local-ip>:8501
    ```

    Open your web browser and navigate to the **Local URL** provided to interact with the ChAI assistant.

---

## Commands Breakdown

* **`llama stack build --template ollama --image-type venv --run`**: This command utilizes `llama-stack` to build and run an environment based on the Ollama template, specifically configured for your virtual environment.
* **`streamlit run app.py`**: This command executes the Streamlit web application (`app.py`), which provides the user interface for interacting with the ChAI assistant.

---

## Troubleshooting

### 1. `ImportError: ...`

If you encounter import errors related to `pydantic` or other Python packages, try the following troubleshooting steps:

* **Reinstall the problematic package, potentially building from source:**

    ```bash
    pip install --no-binary :all: pydantic
    ```

* **Ensure Python Environment Compatibility:** Verify that your active Python environment (`.chenv`) is compatible with the package versions specified in your `requirements.txt` file. You might need to update or downgrade packages if there are conflicts.

### 2. `Permission Denied / File Access Errors`

If you run into permission-related issues, ensure your user has the necessary read and write permissions for the files and directories involved. If necessary, you can attempt to modify permissions using the `chmod` command (e.g., `chmod +x <filename>`). Use `sudo` with caution, as it can have unintended consequences if not used correctly.

---

## Additional Notes

* **Ollama**: Ollama serves as the local inference server, running the `llama3.2:3b` model by default. You can experiment with different models by modifying the `INFERENCE_MODEL` environment variable before running the `llama stack build` command.
* **Streamlit**: Streamlit provides the interactive front-end UI that displays the ChAI assistant's responses and allows you to input queries.
* **LlamaStack Client**: While the guide mentions LlamaStack installation, the direct client usage in the provided steps isn't explicit. LlamaStack is being used behind the scenes by the `llama stack build` command to manage the model and inference setup with Ollama.

---

