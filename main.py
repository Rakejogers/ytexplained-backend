from fastapi import FastAPI, status, HTTPException
import openai
from youtube_transcript_api import YouTubeTranscriptApi
from fastapi.middleware.cors import CORSMiddleware
import time
import tiktoken
import os


openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

origins = ["*"] 
# [
#     "https://rakejogers.github.io",
#     "http://127.0.0.1:5500/",
#     "https://jakerogers.engineer"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# test link https://www.youtube.com/watch?v=DXDe-2BC4cE

@app.get("/ytexplainer")
def root(yt_id):
  if(yt_id!="false"):
    try:
      transcript = YouTubeTranscriptApi.get_transcript(yt_id)
    except:
      raise HTTPException(status_code=404, detail="Video not found or does not have transcript")

    text = ""
    for i in transcript:
      text += i['text'] + " "

    def num_tokens_from_string(string: str) -> int:
      """Returns the number of tokens in a text string."""
      encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
      num_tokens = len(encoding.encode(string))
      return num_tokens
    
    if num_tokens_from_string(text) < 16000:
    
      completion = openai.ChatCompletion.create(
          model="gpt-3.5-turbo-16k",
          messages=[
              {"role": "system", "content": "Please provide a concise summary of the YouTube video's content below. Assume the audience is looking for a clear and informative overview of the video. You may include key points, important insights, and any relevant highlights from the transcript. Keep the summary length between 2 to 3 paragraphs. Feel free to rephrase and structure the information for coherence and readability. Be mindful of avoiding redundancy and ensure the summary remains faithful to the video's core message."},
              {"role": "user", "content": text}
          ],
          temperature=.5
      )
      return {"message": completion.choices[0].message.content}
    else:
      raise HTTPException(
          status_code=409, detail="Video is too long!")
  else:
    return {"message": "Please enter a valid Youtube link!!!"}
