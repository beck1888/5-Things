# 5 Things Podcast Maker

## Description
This program creates a podcast with the 5 most important pieces of news from the New York Times. It uses the New York Times API to get the news and the OpenAI Text-to-Speech API to convert the news into audio. The program also uses the `pydub` library to concatenate the audio files and add an intro and outro.

## Installation
1. Clone the repository
2. Install the required packages with `pip install -r requirements.txt`
3. Create a `.env` file in the root directory with the following content:
    ```
    OPENAI_API_KEY=<your-api-key-here-starting-with-sk>
    ```

## Usage
1. Run the program with `python main.py`
    - The program will automatically create all needed files and directories as it needs them

## Credits
- **cache/intro.mp3** | [News End Signature.wav by mansardian](https://freesound.org/s/61322/) -- License: [Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)
- **cache/outro.mp3** | [News jingle by jobro](https://freesound.org/s/169214/) -- License: [Attribution NonCommercial 3.0](https://creativecommons.org/licenses/by-nc/3.0/)