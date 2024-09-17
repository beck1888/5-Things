from app_functions import *

verify_api_key()

clear()

confirm_run()

print("Getting news...")
news = get_news()

print("Formatting news...")
formatted_news = format_news(news)

expanded_news = []

i = 1

for story_package in formatted_news:
    print(f"Expanding story {str(i)} of 5...")
    i += 1
    expanded_news.append(expand_story(story_package))

print("Condensing up the story...")
story_only_script = tidy_up_story(expanded_news)

# TODO: Trim the script to less than 4k characters and remove the placeholders, cues, and other unnecessary text from GPT's output

print("Completing the script...")
full_script = complete_script(story_only_script)

# print(full_script)

LANG = "English"

print("Translating the script...")
if LANG != "English":
    full_script = translate(full_script, target_lang=LANG)
else:
    print("No translation needed.")
    full_script = full_script

print("Generating audio...")
cache = say(full_script, lang=LANG)

print("Appending intro and outro music...")
final_fp = append_intro_and_outro_music(cache)
print(final_fp)