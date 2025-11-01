from flask_cors import CORS
from flask import Flask, request, jsonify
from flask import send_file, url_for
import google.generativeai as genai
import os, json
from langua import EdgeSpeech


app = Flask(__name__)
CORS(app)
Genai_model = "gemini-2.5-flash"
MEMORY_FILE = "story_memory.json"
tts_engine = EdgeSpeech()


class StorySparkAI:
    def __init__(self, api_key, model_name=Genai_model, memory_file=MEMORY_FILE):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.memory_file = memory_file
        self.memory = self.load_memory()

    def load_memory(self):
        # We gonna use this function to load user memory from JSON file.
        if not os.path.exists(self.memory_file):
            return {}
        try:
            with open(self.memory_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    def save_memory(self):
        #ONly to Save User memory to JSON file.
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2)
    def remember_story(self, user, story):
        #to Store the story in memory for that user.
        user_memory = self.memory.get(user, [])
        user_memory.append(story)
        self.memory[user] = user_memory[-5:]  # Keep last 5 stories because of too much memory
        self.save_memory()

    def generate_story(self, user,  prompt, genre, mood, language):
            # Generate a creative short story using Chatgot da simpul.
            # intake past context
        prev_context = self.memory.get(user, [])
        context_text = ""
        if prev_context:
            context_text = "\nHere are your previous stories for inspiration:\n" + "\n---\n".join(prev_context[-2:])

        full_prompt = f"""
    You are StorySpark AI, a creative fiction writer.
    Write a 150-200 word flash fiction story in the {language} language.
    Genre: '{genre}'
    Tone: '{mood}'
    Prompt: "{prompt}"
    Make it original, imaginative, and emotionally engaging.
    {context_text}
    End the story with a satisfying or surprising twist.
    """

        try:
            response = self.model.generate_content(full_prompt)
            story = response.text.strip()
        except Exception as e:
            story = f"[Error generating story: {e}]"

            # Just to Save memory
        if story and "Error" not in story:
            self.remember_story(user, story)

        return story

api_key = "AIzaSyDa6OzM2Ln2FjV7Rugxzbp9tUw_4L_fJwg"
story_ai = StorySparkAI(api_key)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "")
    genre = data.get("genre", "fiction")
    mood = data.get("mood", "neutral")
    user=data.get("user","guest")
    language = data.get("language", "English")
    voice_enabled = bool(data.get("voice", False))

    if not prompt.strip():
        return jsonify({"error": "Sorry Sire ,Prompt cannot be empty."})#4

    if language.lower() not in ["english", "hindi"]:
        return jsonify({"error": "Only English and Hindi is supported."})#4

    try:
        story = story_ai.generate_story(user, prompt, genre, mood, language)
    except Exception as e:
        return jsonify({"error": f"Story generation failed: {e}"})#5

    if voice_enabled:
        try:
            filepath = tts_engine.synthesize(story)
            audio_url = url_for('get_audio', filename=os.path.basename(filepath), _external=True)
            return jsonify({"story": story, "audio_url": audio_url})
        except Exception as e:
            return jsonify({"story": story, "error": f"TTS failed: {e}"}), #5

    return jsonify({"story": story})

@app.route("/audio/<filename>")
def get_audio(filename):
    """Serve generated audio files for playback"""
    return send_file(os.path.join("tts_output", filename), mimetype="audio/mpeg")

def test_the_generate_funcn():
    chatbot = StorySparkAI(api_key="AIzaSyDa6OzM2Ln2FjV7Rugxzbp9tUw_4L_fJwg")
    L = []
    for i in range(5):
        print("enter the promt")
        L.append(input())
    print(chatbot.generate_story(L[0], L[1], L[2], L[3], L[4]))
if __name__ == "__main__":
    app.run(debug=True, port=5000)
    #test_the_generate_funcn()




