# Sonar Analysis Hub 📡 (with Perplexity AI)

**Entry for the Perplexity AI Hackathon**

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Framework-orange.svg)](https://streamlit.io)
[![Perplexity AI](https://img.shields.io/badge/AI-Perplexity%20Sonar-9cf.svg)](https://perplexity.ai)
<!-- Add other badges if relevant (e.g., License: MIT) -->

The Sonar Analysis Hub is a web-based application designed for exploring simulated sonar data, uploading user-specific sonar-related files, and leveraging the analytical capabilities of Perplexity AI's Sonar models for insights and assistance.

Built with Streamlit, it provides an intuitive interface for users to visualize different types of simulated sonar scans (Sea, Land, Air), generate new scan data, upload their own images or data files, and interact with an AI assistant powered by Perplexity AI.

![Sonar Analysis Hub In Action](YOUR_SONAR_GIF_URL_HERE) <!-- Replace with a relevant GIF URL -->

---

## ✨ Features

*   **🤖 Perplexity AI Sonar Assistant:** Interact with an AI assistant to ask questions about sonar principles, data interpretation, target classification, or the hub's functionalities. The AI can also discuss user-uploaded content.
*   **🛰️ Explore Simulated Scan Data:**
    *   Load and visualize details from pre-defined sonar scans (Side-Scan Sonar, GPR, Ultrasonic).
    *   View scan metadata, parameters, summaries, and simulated spectrograms/radargrams.
    *   Examine lists of detected targets with their characteristics.
    *   Download scan data in JSON format.
*   **💡 Simulate New Sonar Scans:**
    *   Configure parameters (sonar type, area, frequency, range/depth, custom notes) to generate new simulated sonar scan data.
    *   View and download the results of these simulations.
    *   Optionally add new simulations to the "Explore Scan Data" list for the current session.
*   **⬆️ Upload & Analyze Sonar Data:**
    *   Upload sonar-related images (PNG, JPG, JPEG) for display.
    *   Upload sonar-related data files (CSV, TXT) for preview.
    *   Engage the Perplexity AI Assistant to discuss uploaded images (by name/reference) or analyze text snippets from uploaded data files.
*   **🛠️ Sonar Technologies Information:**
    *   Access descriptive information about various sonar technologies like Side-Scan Sonar (SSS), Multi-Beam Echosounders (MBES), Ground Penetrating Radar (GPR), Ultrasonic Sensors, and the role of AI in sonar classification.
*   **🎨 Themed UI:** Custom-styled Streamlit interface with a dark, modern aesthetic suitable for data analysis.

---

## 🛠️ Technology Stack

*   **Framework:** Streamlit
*   **AI Model:** Perplexity AI Sonar Models (e.g., `sonar-pro`) via the `openai` Python library.
*   **Data Handling & Numerics:** `pandas`, `numpy`
*   **Plotting & Visualization:** `plotly.express`
*   **Image Handling:** `Pillow` (PIL)
*   **API Interaction (for Perplexity):** `openai`
*   **File Handling:** `io`, `json`
*   **Utilities:** `datetime`, `time`, `re`

---

## 📃 Repository Structure

```
sonar_analysis_hub/
├── .streamlit/
│   ├── secrets.toml          # Your actual API keys (gitignored)
│   └── secrets.toml.example  # Example for API keys
├── app.py                    # Main Streamlit application code
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── .gitignore                # Files to be ignored by Git
```
*(Note: Additional assets like images for the UI could be placed in an `assets/` directory if desired)*

---

## 🚀 Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd sonar_analysis_hub
    ```

2.  **Create and Activate Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    # .\venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Secrets for Perplexity AI:**
    *   If it doesn't exist, create the `.streamlit` directory in the project root: `mkdir .streamlit`
    *   Copy the example secrets file:
        ```bash
        # On Windows (PowerShell):
        # copy .streamlit\secrets.toml.example .streamlit\secrets.toml
        # On macOS/Linux:
        # cp .streamlit/secrets.toml.example .streamlit/secrets.toml
        ```
    *   Open `.streamlit/secrets.toml` with a text editor.
    *   Replace `pplx-YOUR_PERPLEXITY_API_KEY_HERE` with your actual Perplexity AI API key.
        ```toml
        [perplexity_api]
        api_key = "pplx-YOUR_ACTUAL_KEY"
        ```
    *   **IMPORTANT:** The `.gitignore` file is configured to prevent `secrets.toml` from being committed to version control. **Never commit your actual secrets file.**

---

## ▶️ Running the App

Ensure your virtual environment is activated and you are in the project's root directory (`sonar_analysis_hub/`).

Run the Streamlit application using:

```bash
streamlit run app.py
```

The application should then open in your default web browser.

---

## 🤖 AI Integration Notes

*   The AI Assistant leverages Perplexity AI's Sonar models. Ensure your API key is correctly configured.
*   **Image Analysis:** When you upload an image and ask the AI about it, the AI does *not* receive the image data directly. It will attempt to discuss the image based on its filename (if you mention it) and your textual description or query. The system prompt guides the AI on this.
*   **Data File Analysis:** For uploaded CSV or TXT files, a text preview (a snippet of the content) *is* sent to the Perplexity AI model along with your query when you ask it to analyze the file.
*   **Context Handling:** Context from uploaded files (image references or text snippets) is typically cleared after one analysis query to the AI. This helps manage the conversation flow and API usage. You may need to refer to or re-upload a file if you wish to ask multiple, separate questions about it.
```

**Remember to:**

1.  Replace `<your-repository-url>` with the actual URL once you host it.
2.  Find a suitable animated GIF and replace `YOUR_SONAR_GIF_URL_HERE` with its direct URL. You can search on sites like Giphy or create your own.
3.  Review the "Repository Structure" section. If you decide to add an `assets/` folder for images (like the logo `https://i.imgur.com/sQju3dP.jpeg` used in the sidebar), you can mention it there.

This README provides a comprehensive overview for anyone looking to understand, set up, and run your Sonar Analysis Hub application.
