# SpeechToText

SpeechToText is a Python project that uses the OpenAI API to transcribe audio files. This project supports segmenting audio files into smaller intervals and transcribing them individually. It also supports extracting audio from video files before transcribing.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

To use this project, you need Python 3.6 or later.

1. Clone the repository:

git clone https://github.com/username/SpeechToText.git

2. Install the required dependencies:

pip install -r requirements.txt

3. Set up your OpenAI API key in a .env file in the project's root directory:

OPENAI_API_KEY=your_api_key_here

Replace your_api_key_here with your actual OpenAI API key.

## Usage

To use the **SpeechToText** class, simply create an instance and provide the path to the directory containing the audio or video files:
```
transcriber = SpeechToText('path/to/your/audio/files')
```
### Extracting Audio from Video

To extract audio from a video file, use the **extract_audio_from_video** method:
```
transcriber.extract_audio_from_video(file_name='your_video_file.mkv')
```
### Segmenting Audio

To segment an audio file into smaller intervals, use the **segment_audio** method:
```
segmented_files, _ = transcriber.segment_audio(file_name='your_audio_file.mp3', interval=5)
```

Here the file is segmented in 5 minutes files.
**segmented_files** will be a list of paths to your segmented files

### Transcribe Audio

To transcribe audio

```
transcriber.multiple_audio_transcription(segmented_files)
```

This will create a .txt file with the transcription