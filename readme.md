# Threat Analytics Tool

The Threat Analysis Tool is an advanced analytics solution designed to extract entities and relationships from unstructured text data. Built to address the challenges of analyzing complex threat-related information, this tool enables users to uncover meaningful insights and visualize intricate relationships throught network graphs within the data. The tool uses GPT-4o LLM model for threat analysis and sorting.

## Live Deployment

You can access the deployed app here:  
👉 [https://donki-git-main-regmcs-projects.vercel.app/](https://donki-git-main-regmcs-projects.vercel.app/)

---

## Running Locally

1. **Clone the repository:**

   ```bash
   git clone https://github.com/RegMCS/donki
   cd donki
   ```
2. **Creating a Virtual Environment**
   ```sh
   python3 -m venv .venv
   ```
3. **Activate the virtual environment:**
   * On Windows:
   ```sh
   .venv\Scripts\activate
   ```
   * On macOS and Linux:
   ```sh
   source .venv/bin/activate
   ```
4. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Flask app**

   ```bash
   flask run app.py
   ```
   OR
   ```bash
   python app.py
   ```

6. **Open your browser:**

   ```
   http://localhost:5000
   ```


