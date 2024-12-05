# YouTube Video Summarizer

A Gradio-based web minimal app that generates Chinese summaries of YouTube video transcripts using an LLM API.

## Features

- Extract YouTube video ID from URLs or direct input
- Download and process video transcripts (supports English and Chinese)
- Generate structured summaries in Chinese using LLM
- User-friendly web interface powered by Gradio

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Copy config.example.toml to config.toml and update with your API credentials:
   ```bash
   cp config.example.toml config.toml
4. Run the application:
   ```bash
   python app.py

## Configuration
The application uses a TOML configuration file for API settings. Update config.toml with:

- api_key: Your LLM API key
- base_url: API endpoint URL
- model_name: LLM model name (google gemini flash 8b works well)