# VoiceOps 2026 — ZentroMart AI Customer Support Agent

An educational capstone implementation using the **provided synthetic ZentroMart data**. It includes current-policy retrieval, a conversational LLM, verified order lookup, ticket creation helper, and Gnani-only speech recognition/synthesis.

## What is included

- `dataset/data/`: seven CSV tables (customers, orders, items, products, pincodes, holidays, support logs).
- `dataset/kb/`: 21 original knowledge documents, including the superseded returns policy (excluded from retrieval).
- `dataset/practice/`: two evaluation CSVs.
- `dataset/tools/`: original `lookup_order` and `create_ticket` mock tools.
- `src/agent.py`: TF-IDF retrieval, grounded LLM prompting, order verification and conversation memory.
- `src/voice.py`: Gnani STT and TTS only.
- `run.py`: text chat, dataset checks and batch audio runner.
- `ui.py`: optional Gradio text and microphone interface.

## Run in VS Code (Windows PowerShell)

1. Extract the ZIP, open the extracted folder in VS Code and open **Terminal > New Terminal**.
2. Install Python 3.14, then run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

3. Edit `.env`: add **your own** `GEMINI_API_KEY` and `GNANI_API_KEY`. Do not share this file.
4. Check the dataset and index:

```powershell
.\.venv\Scripts\python.exe run.py validate --dataset ./dataset
.\.venv\Scripts\python.exe run.py inspect --dataset ./dataset
```

5. Start text chat:

```powershell
.\.venv\Scripts\python.exe run.py chat --dataset ./dataset
```

6. Start the web UI:

```powershell
.\.venv\Scripts\python.exe ui.py
```

Open the local Gradio URL printed in the terminal. Voice requires a valid Gnani key and microphone permission.

## Run in Google Colab

Upload the complete ZIP to a Colab notebook, then run cells in order:

```python
from google.colab import files
files.upload()  # select ZentroMart_VoiceOps_2026_Complete.zip
```

```python
!unzip -q ZentroMart_VoiceOps_2026_Complete.zip -d /content
%cd /content/ZentroMart_VoiceOps_2026_Rebuilt
!pip -q install -r requirements.txt
!python run.py validate --dataset ./dataset
```

```python
import os
from getpass import getpass
os.environ['GEMINI_API_KEY']=getpass('OpenAI API key: ')
os.environ['GNANI_API_KEY']=getpass('Gnani API key: ')
from src.agent import Agent
agent=Agent('./dataset')
print(agent.respond('What is the return policy?')['reply'])
```

For uploaded audio, place clips in `sample_audio/` and run:

```python
!python run.py batch --dataset ./dataset --audio-dir ./sample_audio --output-dir ./outputs
```

## Batch evaluation command

```bash
python run.py batch --dataset ./dataset --audio-dir ./sample_audio --output-dir ./outputs
```

Each processed audio clip writes a WAV response and a JSON record with transcription, answer, and retrieved source filenames/scores.

## Important limitations

- **Live LLM and Gnani API calls have not been verified** in this rebuild; they require valid keys and service access.
- The project implements a basic TF-IDF retrieval baseline, not an embedding/vector database. It should be improved for the capstone's vector-retrieval expectations.
- Ticket creation is available as `Agent.ticket(summary)` but is **not automatically selected by the LLM**. Do not claim automatic ticket handover.
- Order verification uses the provided educational mock tool, not production authentication.
- The PDF report is a project description, **not evidence of measured LLM or voice quality**.
- The capstone's submission ZIP must **exclude the dataset copy** and include a real demo video, actual evaluation scores, and a public Git URL. These are not yet provided.

## Privacy and safety

Only use the synthetic provided records. Do not commit `.env` or API keys. Do not use any STT/TTS provider other than Gnani for this capstone.
Demo Video

Demo video recordings: https://drive.google.com/drive/folders/1ERCLunTgAKFKu24JuBF93ZIYgoL9zJ99

The folder contains the project demonstration recordings.
