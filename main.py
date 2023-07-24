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

# text link https://www.youtube.com/watch?v=DXDe-2BC4cE

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
    time.sleep(5)
    return {"message": "The YouTuber talks about their recent experiences, including moving and dealing with technical issues. They mention that their YouTube channel has seen significant growth and express their desire to improve public transportation in their city. They discuss their plans to replace certain bus lines with tram lines and make adjustments to the infrastructure. They encounter challenges and frustrations in implementing these changes but eventually find solutions. They express satisfaction with the increased capacity and hope that the improvements will help alleviate traffic issues.In this video, the YouTuber shares their personal experiences and updates while also showcasing their gameplay of a city-building game. They discuss their channel's growth and their intention to improve public transportation in the game. They demonstrate their planning and decision-making process, as well as the challenges they face in implementing their ideas. Ultimately, they find solutions and express satisfaction with the results. The video provides a mix of personal anecdotes, gaming content, and a glimpse into the YouTuber's creative problem-solving skills."}
