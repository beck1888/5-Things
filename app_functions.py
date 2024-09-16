import feedparser
import dotenv
import os
from openai import OpenAI
from datetime import datetime
from pathlib import Path
import random
from pydub import AudioSegment

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def confirm_run():
    code = str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9))
    print("WARNING: This script will generate a lot of expensive API calls. Please confirm you want to run this script by entering the following code: " + code)
    choice = input(">> ")
    if choice == code:
        return True
    else:
        exit("Code did not match. Execution halted.")

def verify_api_key():
    try:
        dotenv.load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None or "sk" not in api_key:
            exit("API key not found or invalid. Please check your .env file and add a valid OpenAI API key.")
        else:
            return True
    except:
        exit("API key not found or invalid. Please check your .env file and add a valid OpenAI API key.")

def get_news(site_rss_url="https://rss.nytimes.com/services/xml/rss/nyt/US.xml", read_to=5):
    # Parse the feed
    feed = feedparser.parse(site_rss_url)

    result = {}

    # GET Head
    result["section"] = feed.feed.title

    # Find max entries
    result["max_entries"] = len(feed.entries)

    # Check how many entries are available
    max_entries = len(feed.entries)

    # Find how many entries to read
    if read_to > max_entries:
        read_to = max_entries
    else:
        read_to = read_to

    # GET Entries (5)
    index = 0
    for entry in feed.entries[:read_to]:
        index += 1
        result[f"story_{str(index)}"] = {
            "title": entry.title,
            "summary": entry.summary
        }

    # Specify number of entries
    result["num_entries"] = index

    r_value = ""

    for key, value in result.items():
        r_value += f"{key}: {value}\n"

    return result

def format_news(news) -> list:
    result = []

    for key, value in news.items():
        if key.startswith("story_"):
            headline = key.removeprefix("story_")
            title = value['title'].lstrip(".?")
            summary = value['summary']
            result.append(f"Headline {headline}: {title}: {summary}")

    return result

def get_api_key() -> str:
    dotenv.load_dotenv()
    return os.getenv("OPENAI_API_KEY")

def expand_story(story: str) -> str:
    client = OpenAI(api_key=get_api_key())

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Please expand this into a two sentences spoken like a news anchor. Start with the headline number such as 'First up' or 'Our second story'. Use your current knowledge to expand the story. Write no more that 50 words."},
            {
                "role": "user",
                "content": story
            }
        ]
    )

    return response.choices[0].message.content

def tidy_up_story(stories: list) -> str:
    story_string = "\n".join(stories)

    client = OpenAI(api_key=get_api_key())

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Please make this into a coherent news broadcast script of about 200 words. Present it as a news anchor would, in a formal and direct manner. Do not add an intro. Do not add any placeholders. Do not add any cues. Do not add any other unnecessary text. This script is going to be fed into a TTS system directly. Do not add any cues or placeholders."},
            {
                "role": "user",
                "content": story_string
            }
        ]
    )

    return response.choices[0].message.content

def _get_time_of_day():
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "morning"
    elif 12 <= current_hour < 17:
        return "afternoon"
    elif 17 <= current_hour < 21:
        return "evening"
    else:
        return "early morning"
    
def _get_formatted_date():
    now = datetime.now()
    day_name = now.strftime("%A")
    month_name = now.strftime("%B")
    day = now.strftime("%d").lstrip('0')
    year = now.strftime("%Y")

    # Convert day to ordinal
    if day == "1" or day.endswith("1") and not day.endswith("11"):
        day += "st"
    elif day == "2" or day.endswith("2") and not day.endswith("12"):
        day += "nd"
    elif day == "3" or day.endswith("3") and not day.endswith("13"):
        day += "rd"
    else:
        day += "th"

    return f"{day_name}, {month_name} {day}, {year}"

def complete_script(story_script):
    time_of_day = _get_time_of_day()
    disclaimer = "HEADS UP: The voice you are hearing is a computer generated voice, not a human."
    header = f"Good {time_of_day} from Beck's 5 things, powered by The New York Times. My name is Quantum and here are the top 5 things you need to know for {_get_formatted_date()}."
    footer = "That's all for now. Come back later today to catch our next show. This is Quantum, signing off."
    full_script = f"{disclaimer} {header}\n\n{story_script}\n\n{footer}"
    return full_script

def translate(text, target_lang = "Spanish"):
    client = OpenAI(api_key=get_api_key())

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Please translate this input to {target_lang}. Keep the news anchor like tone, but do not add any cues or placeholders. Do not add anything extra. Keep about the same length or shorter, but do not make it longer."},
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return response.choices[0].message.content

def _get_time():
    now = datetime.now()
    return now.strftime("%I:%M %p").lstrip('0')

def say(text, lang, voice="nova") -> str:
    # Initialize the OpenAI API client
    client = OpenAI(api_key=get_api_key())

    # Structure the request
    response = client.audio.speech.create(
    model="tts-1",
    voice=voice,
    input=text
    )

    # Create the cache directory if it doesn't exist
    if not os.path.exists(Path(__file__).parent / "cache"):
        os.makedirs(Path(__file__).parent / "cache")

    file_id = _get_formatted_date() + f" at {_get_time()} 5 Things " + lang

    # Save the audio file
    file_name = speech_file_path = Path(__file__).parent / "cache" / f"{file_id}.mp3"
    response.write_to_file(speech_file_path)

    return "Your file is at: cache/" + str(file_id) + ".mp3"

def append_intro_and_outro_music(file_path):
    file_path = file_path.removeprefix("Your file is at: ")
    intro = "sources/intro.mp3"
    outro = "sources/outro.mp3"

    # Load the intro, outro, and main audio files
    intro_audio = AudioSegment.from_mp3(intro)
    outro_audio = AudioSegment.from_mp3(outro)
    main_audio = AudioSegment.from_mp3(file_path)

    # Concatenate the audio files
    final_audio = intro_audio + main_audio + outro_audio

    # Create the podcasts directory if it doesn't exist
    podcasts_dir = Path(__file__).parent / "podcasts"
    if not podcasts_dir.exists():
        podcasts_dir.mkdir(parents=True)

    # Save the final audio file
    final_file_path = podcasts_dir / Path(file_path).name
    final_audio.export(final_file_path, format="mp3")

    return f"Your file is at: podcasts/{final_file_path.name}"