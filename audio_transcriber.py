#!/usr/bin/env python3
"""
Audio Transcription Tool using AssemblyAI
Transcribes audio files and saves the output in various formats
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime

# Try to import python-dotenv for .env file support
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # dotenv not installed, will rely on system env vars

class AudioTranscriber:
    """Handle audio transcription using AssemblyAI API"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.assemblyai.com"
        self.headers = {
            "authorization": api_key,
            "content-type": "application/json"
        }
    
    def upload_file(self, file_path):
        """Upload local audio file to AssemblyAI"""
        print(f"📤 Uploading file: {file_path}")
        
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{self.base_url}/v2/upload",
                headers=self.headers,
                data=f
            )
        
        if response.status_code != 200:
            raise Exception(f"Upload failed: {response.text}")
        
        upload_url = response.json()["upload_url"]
        print(f"✅ File uploaded successfully")
        return upload_url
    
    def create_transcript(self, audio_url, config=None):
        """Create a new transcription job"""
        data = {
            "audio_url": audio_url,
            "speech_model": "best"  # Using best model for highest accuracy
        }
        
        # Add any additional configuration
        if config:
            data.update(config)
        
        response = requests.post(
            f"{self.base_url}/v2/transcript",
            json=data,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Transcription request failed: {response.text}")
        
        return response.json()
    
    def poll_transcript(self, transcript_id):
        """Poll for transcription completion"""
        polling_endpoint = f"{self.base_url}/v2/transcript/{transcript_id}"
        
        print("\n⏳ Transcribing audio...")
        while True:
            response = requests.get(polling_endpoint, headers=self.headers)
            result = response.json()
            
            status = result['status']
            if status == 'completed':
                print("✅ Transcription completed!")
                return result
            elif status == 'error':
                raise RuntimeError(f"Transcription failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"   Status: {status}... waiting...")
                time.sleep(3)
    
    def get_paragraphs(self, transcript_id):
        """Get transcript broken down by paragraphs"""
        url = f"{self.base_url}/v2/transcript/{transcript_id}/paragraphs"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get paragraphs: {response.text}")
        
        return response.json()['paragraphs']
    
    def get_sentences(self, transcript_id):
        """Get transcript broken down by sentences"""
        url = f"{self.base_url}/v2/transcript/{transcript_id}/sentences"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get sentences: {response.text}")
        
        return response.json()['sentences']

def format_timestamp(milliseconds):
    """Convert milliseconds to readable timestamp"""
    seconds = milliseconds / 1000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    else:
        return f"{minutes:02d}:{secs:02d}.{millis:03d}"

def save_transcription(transcript_data, output_path, format_type='full'):
    """Save transcription to file in specified format"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = Path(output_path).stem
    
    if format_type == 'full':
        # Save complete transcription
        output_file = f"{base_name}_transcript_{timestamp}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Transcription generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Transcript ID: {transcript_data['id']}\n")
            f.write(f"Duration: {transcript_data.get('audio_duration', 'Unknown')} seconds\n")
            f.write(f"Confidence: {transcript_data.get('confidence', 'N/A')}\n")
            f.write("="*50 + "\n\n")
            f.write(transcript_data['text'])
        print(f"📄 Full transcript saved to: {output_file}")
        return output_file
    
    elif format_type == 'json':
        # Save complete JSON response
        output_file = f"{base_name}_transcript_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, indent=2)
        print(f"📄 JSON transcript saved to: {output_file}")
        return output_file

def save_paragraphs(paragraphs, output_path):
    """Save paragraph-formatted transcription"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = Path(output_path).stem
    output_file = f"{base_name}_paragraphs_{timestamp}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Paragraph-formatted transcription\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")
        
        for i, para in enumerate(paragraphs, 1):
            f.write(f"[Paragraph {i}] ")
            f.write(f"({format_timestamp(para['start'])} - {format_timestamp(para['end'])})\n")
            if 'speaker' in para and para['speaker']:
                f.write(f"Speaker: {para['speaker']}\n")
            f.write(f"{para['text']}\n\n")
    
    print(f"📄 Paragraph transcript saved to: {output_file}")
    return output_file

def save_sentences(sentences, output_path):
    """Save sentence-formatted transcription"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = Path(output_path).stem
    output_file = f"{base_name}_sentences_{timestamp}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Sentence-formatted transcription\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")
        
        for i, sent in enumerate(sentences, 1):
            f.write(f"[{i}] {format_timestamp(sent['start'])}: {sent['text']}\n")
    
    print(f"📄 Sentence transcript saved to: {output_file}")
    return output_file

def save_srt_subtitles(sentences, output_path):
    """Save transcription as SRT subtitle file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = Path(output_path).stem
    output_file = f"{base_name}_subtitles_{timestamp}.srt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, sent in enumerate(sentences, 1):
            # SRT format timestamps
            start = format_timestamp(sent['start']).replace('.', ',')
            end = format_timestamp(sent['end']).replace('.', ',')
            
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{sent['text']}\n\n")
    
    print(f"📄 SRT subtitles saved to: {output_file}")
    return output_file

def main():
    parser = argparse.ArgumentParser(
        description='Transcribe audio files using AssemblyAI API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic transcription:
    %(prog)s audio.mp3 --api-key YOUR_API_KEY
  
  Save all formats:
    %(prog)s audio.mp3 --api-key YOUR_API_KEY --all-formats
  
  Specific formats:
    %(prog)s audio.mp3 --api-key YOUR_API_KEY --paragraphs --srt
  
  Use environment variable for API key:
    export ASSEMBLYAI_API_KEY=YOUR_API_KEY
    %(prog)s audio.mp3
        """
    )
    
    # Required arguments
    parser.add_argument('audio_file', help='Path to audio file (MP3, WAV, etc.)')
    
    # API key handling
    parser.add_argument('--api-key', type=str, 
                       help='AssemblyAI API key (or set ASSEMBLYAI_API_KEY env var)')
    
    # Output format options
    parser.add_argument('--json', action='store_true',
                       help='Save full JSON response')
    parser.add_argument('--paragraphs', action='store_true',
                       help='Save paragraph-formatted transcript')
    parser.add_argument('--sentences', action='store_true',
                       help='Save sentence-formatted transcript')
    parser.add_argument('--srt', action='store_true',
                       help='Save SRT subtitle file')
    parser.add_argument('--all-formats', action='store_true',
                       help='Save transcript in all available formats')
    
    # Additional options
    parser.add_argument('--no-timestamps', action='store_true',
                       help='Exclude timestamps from output')
    parser.add_argument('--speaker-labels', action='store_true',
                       help='Enable speaker diarization (identify different speakers)')
    
    args = parser.parse_args()
    
    # Get API key from argument or environment
    api_key = args.api_key or os.environ.get('ASSEMBLYAI_API_KEY')
    if not api_key:
        print("Error: AssemblyAI API key is required.")
        print("Provide it via --api-key argument or set ASSEMBLYAI_API_KEY environment variable.")
        print("\nTo use a .env file, install python-dotenv:")
        print("  pip install python-dotenv")
        sys.exit(1)
    
    # Validate audio file exists
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"Error: Audio file not found: {args.audio_file}")
        sys.exit(1)
    
    # Initialize transcriber
    transcriber = AudioTranscriber(api_key)
    
    try:
        print(f"\n🎤 Audio Transcription Tool")
        print(f"📁 Input file: {audio_path.name}")
        print(f"📊 File size: {audio_path.stat().st_size / 1024 / 1024:.2f} MB")
        print("-" * 50)
        
        # Upload file
        upload_url = transcriber.upload_file(str(audio_path))
        
        # Configure transcription
        config = {}
        if args.speaker_labels:
            config['speaker_labels'] = True
            print("🔊 Speaker diarization enabled")
        
        # Create transcription
        transcript_response = transcriber.create_transcript(upload_url, config)
        transcript_id = transcript_response['id']
        print(f"📋 Transcript ID: {transcript_id}")
        
        # Wait for completion
        transcript_data = transcriber.poll_transcript(transcript_id)
        
        # Determine which formats to save
        save_all = args.all_formats
        
        # Always save the basic text transcript
        save_transcription(transcript_data, str(audio_path), 'full')
        
        # Save additional formats as requested
        if args.json or save_all:
            save_transcription(transcript_data, str(audio_path), 'json')
        
        if args.paragraphs or save_all:
            paragraphs = transcriber.get_paragraphs(transcript_id)
            save_paragraphs(paragraphs, str(audio_path))
        
        if args.sentences or save_all:
            sentences = transcriber.get_sentences(transcript_id)
            save_sentences(sentences, str(audio_path))
        
        if args.srt or save_all:
            if not (args.sentences or save_all):
                sentences = transcriber.get_sentences(transcript_id)
            save_srt_subtitles(sentences, str(audio_path))
        
        print(f"\n✅ Transcription complete!")
        print(f"📊 Duration: {transcript_data.get('audio_duration', 'Unknown')} seconds")
        print(f"🎯 Confidence: {transcript_data.get('confidence', 'N/A')}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
