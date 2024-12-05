import gradio as gr
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import logging
import re
import toml
import json
import requests


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

try:
    config = toml.load("config.toml")
except FileNotFoundError:
    config = toml.load("config.example.toml")


def download_and_format_transcript(video_id):
    logging.info(f"Attempting to download transcript for video ID: {video_id}")
    # Get the transcript
    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=["en", "zh-CN"],
        )
        logging.info("Successfully downloaded transcript")
    except Exception as e:
        error_message = f"🚨 Error downloading transcript: {str(e)}"
        logging.error(error_message)
        return gr.Error(error_message)

    # Format the transcript to JSON
    logging.info("Formatting transcript to text")
    formatter = TextFormatter()
    formatted_transcript = formatter.format_transcript(transcript)
    logging.info("Successfully formatted transcript")

    return formatted_transcript


def call_llm_api(prompt):
    logging.info("Initiating LLM API call")
    api_key = config["api"]["api_key"]
    base_url = config["api"]["base_url"]
    model_name = config["api"]["model_name"]

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {"model": f"{model_name}", "messages": [{"role": "user", "content": prompt}]}

    try:
        response = requests.post(base_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for bad status codes
        message = response.json()["choices"][0]["message"]["content"]
        logging.info("Successfully received LLM API response")
        return message
    except requests.exceptions.RequestException as e:
        error_message = f"Error calling LLM API: {str(e)}"
        logging.error(error_message)
        return gr.Error(error_message)


def process_video(video_id):
    logging.info(f"Starting video processing for ID: {video_id}")
    transcript = download_and_format_transcript(video_id)
    if isinstance(transcript, gr.Error):
        return transcript
    logging.info("Preparing prompt for LLM")
    prompt = (
        "<rule>1.Divide the transcript into its main sections or topics and provide a brief summary for each. 2. Respond in Chinese</rule><content>"
        + transcript
        + "</content>"
    )
    return call_llm_api(prompt)


def extract_youtube_video_id(user_input):
    pattern = r"(?:https?:\/\/)?(?:www\.)?youtu(?:\.be|be\.com)\/(?:watch\?v=|embed\/|v\/|.+\?v=)?([^&\n?#]+)"

    match = re.search(pattern, user_input)
    if match:
        return match.group(1)  # 返回捕获组中的视频ID
    return user_input

def summarize_video(user_input):
    logging.info("Starting video summarization process")
    video_id = extract_youtube_video_id(user_input)
    logging.info(f"Parsed video ID: {video_id}")
    result = process_video(video_id)
    logging.info("Completed video summarization process")
    return result


with gr.Blocks() as demo:
    gr.Markdown("# YouTube Video Summarizer")
    gr.Markdown("Enter a YouTube video ID to get a summary of its main sections in Chinese.")

    with gr.Row():
        input_text = gr.Textbox(label="YouTube Video ID/URL", scale=4)
        submit_btn = gr.Button("Summarize", scale=1, variant="primary")

    output_text = gr.Textbox(label="Summary", lines=20, render="markdown")

    submit_btn.click(fn=summarize_video, inputs=input_text, outputs=output_text)

if __name__ == "__main__":
    demo.launch()
