# IT Support AI Chatbot

This project implements an AI-powered IT support chatbot designed to assist users with common IT issues. It leverages natural language processing, intent recognition, and a knowledge base to provide helpful and informative responses.

## Folder Structure

it_support_chatbot/
├── chatbot/
│   ├── caching.py
│   ├── intent_handler.py
│   ├── knowledge.py
│   ├── nl_generation.py
│   ├── init.py
│   └── model_cache/
├── knowledge_docs/
├── templates/
│   └── index.html
├── data/
│   └── intents.json
├── app.py
├── README.md
├── details.txt
└── requirements.txt


*   **`chatbot/`**: Contains core chatbot logic including caching, intent handling, knowledge base interaction, and natural language generation.
*   **`knowledge_docs/`**:  Directory to store IT support documentation files (PDFs, TXT files, DOCX files) that the chatbot uses for its knowledge base.
*   **`templates/`**:  Holds the `index.html` file, which is the HTML template for the chatbot's user interface.
*   **`data/`**: Contains data files like `intents.json`, which defines the chatbot's intents and associated patterns.
*   **`app.py`**: The main Flask application that runs the chatbot.
*   **`README.md`**: This file, providing project information and setup instructions.
*   **`details.txt`**: A simple text file summarizing key project details.
*   **`requirements.txt`**: Lists Python dependencies for easy installation.

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone [repository_url]
    cd it_support_chatbot
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Place your IT documentation in `knowledge_docs/` folder.**  The chatbot will use these files to build its knowledge base. Supported file types are `.pdf`, `.txt`, and `.docx`.

5.  **Configure Intents in `data/intents.json`.**  Modify this file to define the intents your chatbot should recognize, their patterns, associated scripts, and conversational flows. Refer to the structure of the existing `intents.json` for the format.

## Running the Chatbot

1.  **Navigate to the project directory:**

    ```bash
    cd it_support_chatbot
    ```

2.  **Run the Flask application:**

    ```bash
    python app.py
    ```

3.  **Access the chatbot in your browser:** Open your web browser and go to `http://localhost:5000`.

## Code Explanation

### `chatbot/caching.py`

*   Implements the `EmbeddingCache` class.
*   Uses `SentenceTransformer` to generate sentence embeddings.
*   Caches embeddings to avoid redundant calculations and improve performance.

### `chatbot/intent_handler.py`

*   Contains the `IntentHandler` class, responsible for:
    *   Loading and validating intents from `intents.json`.
    *   Precomputing embeddings for intent patterns for efficient intent classification.
    *   Classifying user queries to identify the most likely intent.
    *   Handling queries based on identified intent, including:
        *   Executing Python scripts defined in intents.
        *   Initiating and managing conversational flows for troubleshooting.
        *   Interacting with the knowledge base for RAG (Retrieval-Augmented Generation) responses.
*   Uses cosine similarity for intent classification.
*   Includes error handling and logging for script execution and intent processing.

### `chatbot/knowledge.py`

*   Defines the `KnowledgeBase` class.
*   Uses Langchain and FAISS (Facebook AI Similarity Search) to create and query a vector store from the documents in the `knowledge_docs/` folder.
*   Employs `HuggingFaceEmbeddings` for document and query embeddings.
*   Supports loading `.pdf`, `.txt`, and `.docx` documents.
*   Provides a `search` method to perform similarity searches on the knowledge base and retrieve relevant document chunks.

### `chatbot/nl_generation.py`

*   Implements the `ResponseGenerator` class.
*   Utilizes a pre-trained language model (`google/flan-t5-large` from Hugging Face Transformers) for generating natural language responses.
*   Includes methods for:
    *   `enhance_rag_response`:  Generates responses based on retrieved documents from the knowledge base, using the RAG approach. It filters, cleans, and formats the document content to generate precise and context-aware answers.
    *   `humanize`: Simplifies technical text into more human-readable language.
*   Features text chunking to handle long texts and response formatting for better readability (Markdown, headers, lists, code blocks).

### `app.py`

*   Sets up the Flask web application.
*   Initializes core chatbot components: `EmbeddingCache`, `KnowledgeBase`, `ResponseGenerator`, and `IntentHandler`.
*   Defines API endpoints:
    *   `/`:  Serves the `index.html` frontend.
    *   `/api/chat`:  Handles POST requests for chat messages. It receives user queries, processes them using `IntentHandler`, and returns JSON responses with chatbot responses and response types.
*   Includes basic profiling using `cProfile` to identify performance bottlenecks during app startup and execution.
*   Configures logging and environment variables for TensorFlow and tokenizers.

### `templates/index.html`

*   Provides the HTML structure and JavaScript for the chatbot's user interface.
*   Uses a simple and clean design with CSS for styling.
*   Includes JavaScript functions to:
    *   Toggle between "Script Mode" and "Knowledge Base Mode".
    *   Send user messages to the `/api/chat` endpoint.
    *   Display chatbot responses in the chat container.
    *   Show typing indicators while the bot is processing.
    *   Handle user input and display messages in a user-friendly manner.
*   Uses `marked.js` library to render Markdown formatted responses from the chatbot.

### `data/intents.json`

*   A JSON file that defines the intents the chatbot can recognize and handle.
*   Each intent includes:
    *   `tag`: A unique identifier for the intent (e.g., "greeting", "password_reset").
    *   `patterns`: A list of example user queries that trigger this intent.
    *   `script` (optional): Path to a Python script to execute when this intent is matched.
    *   `flow` (optional): Defines a conversational flow for troubleshooting, consisting of a series of questions and a final script.

### `knowledge_docs/`

*   This folder is expected to be populated with your IT support documentation.
*   The chatbot will automatically index these documents to answer user queries related to the knowledge base.

## Requirements

*   Python 3.x
*   The Python libraries listed in `requirements.txt`.

## Potential Improvements

*   **Enhance Intent Recognition:**  Improve the accuracy of intent classification by adding more patterns, using more sophisticated NLP techniques, or fine-tuning the Sentence Transformer model.
*   **Expand Knowledge Base:** Add more comprehensive and up-to-date documentation to the `knowledge_docs/` folder to improve the chatbot's knowledge and response quality.
*   **Improve Response Generation:**  Experiment with different language models, prompting strategies, and response formatting to generate more helpful, human-like, and accurate responses.
*   **Implement User Authentication and Session Management:** For more complex applications, consider adding user authentication and more robust session management.
*   **Add Testing:** Implement unit tests and integration tests to ensure the reliability and functionality of the chatbot.
*   **Deployment:**  Containerize the application using Docker for easier deployment and scalability. Explore cloud deployment options (e.g., AWS, Google Cloud, Azure).
*   **UI/UX Enhancements:**  Improve the user interface with features like a clearer mode indicator, better styling, and more interactive elements.
*   **Error Handling and Logging:** Enhance error handling and logging throughout the application for better debugging and monitoring.


---
## 2. `details.txt` File Content:

```text
Project Title: IT Support AI Chatbot

Overview:
This project is an AI-powered IT support chatbot designed to help users with common IT issues. It uses natural language processing, intent recognition, and a knowledge base to provide assistance.

Key Technologies:
- Python
- Flask (Web Framework)
- Sentence Transformers (Sentence Embeddings)
- Hugging Face Transformers (FLAN-T5 Language Model)
- Langchain (Knowledge Base Integration)
- FAISS (Vector Database)

Quick Start:
1. Ensure you have Python installed.
2. Install dependencies: `pip install -r requirements.txt`
3. Place your documentation in the 'knowledge_docs/' folder.
4. Run the application: `python app.py`
5. Access the chatbot in your browser: http://localhost:5000

Contact:
[Binit Jha]
[binitjha2000@gmail.com]