# Tunisia Real-Estate Demand Intelligence (MVP Foundation)

## Project Description
This project is the Phase 0 foundation for a Streamlit-based real-estate demand intelligence platform focused on Tunisia.

Current scope is limited to project setup and a minimal landing page.

## Project Structure
```
.
├── app.py
├── data/
├── pages/
├── requirements.txt
├── README.md
└── src/
```

## Setup
1. Create and activate a virtual environment:
   - macOS/Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run the App
```bash
streamlit run app.py
```

After running the command, Streamlit should open a simple landing page confirming:
`Phase 0 setup complete.`
