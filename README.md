# Sonar Analysis Hub 📡 (with Perplexity AI)

A Streamlit web application for visualizing simulated sonar data, uploading user data for AI-assisted analysis, and learning about sonar technologies. This version integrates Perplexity AI for its AI Assistant capabilities.

## Features

*   **Explore Simulated Scans:** View pre-defined sonar scan data (Sea, Land, Air).
*   **Simulate New Scans:** Generate new sonar data based on user-defined parameters.
*   **Upload & Analyze:**
    *   Upload sonar-related images (PNG, JPG).
    *   Upload basic sonar data files (CSV, TXT).
    *   Utilize the Perplexity AI Assistant in the sidebar to discuss uploaded content (images are discussed by name/reference, text data snippets are sent to the AI).
*   **Sonar Technologies:** Information on various sonar systems and AI applications in the field.
*   **Perplexity AI Assistant:** Ask general sonar-related questions or request analysis of uploaded content.

## Prerequisites

*   Python 3.8+
*   Git (for cloning the repository)

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd sonar_analysis_hub
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # For Unix/macOS
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Keys:**
    *   Create a `.streamlit` directory if it doesn't exist: `mkdir .streamlit`
    *   Copy the example secrets file: `cp .streamlit/secrets.toml.example .streamlit/secrets.toml`
    *   Open `.streamlit/secrets.toml` and replace `"pplx-YOUR_PERPLEXITY_API_KEY_HERE"` with your actual Perplexity AI API key.

## Running the Application

Once the setup is complete, you can run the Streamlit application:

```bash
streamlit run app.py
```
The application should open in your web browser.

## AI Integration Notes
The AI Assistant uses the Perplexity AI API (models like sonar-pro).

When analyzing uploaded images, the AI does not receive the image data directly. It relies on your textual questions, any filename you mention, and its general knowledge to respond.

When analyzing uploaded data files (CSV, TXT), a text preview of the file's content is sent to the AI along with your query.

Context from uploaded files/images is cleared after each analysis query to the AI to manage token usage and focus.

## Project Structure
sonar_analysis_hub/
├── .streamlit/
│   ├── secrets.toml.example  # Example for API keys
│   └── secrets.toml          # Your actual API keys (gitignored)
├── app.py                    # Main Streamlit application code
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── .gitignore                # Files to be ignored by Git

Contributing
(Optional: Add guidelines if you plan for others to contribute.)
License
(Optional: Add a license file if you wish, e.g., MIT, Apache 2.0.)

