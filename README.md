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
