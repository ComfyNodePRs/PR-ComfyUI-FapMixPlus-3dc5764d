# fapMixNode.py

import os
import subprocess
import shutil
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

class fapMix:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio_input_dir": ("DIRECTORY_PATH", {"default": "/path/to/default_input_directory"}),
                "output_dir": ("DIRECTORY_PATH", {"default": "/path/to/default_output_directory"}),
                "url": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("DIRECTORY_PATH",)  # Return type to pass the output directory
    FUNCTION = "process_audio"
    CATEGORY = "Audio Processing"
    NAME = "fapMix"

    def process_audio(self, audio_input_dir, output_dir, url):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        main_output_dir = os.path.join(output_dir, f"output_{timestamp}")
        os.makedirs(main_output_dir, exist_ok=True)
        
        input_dir = audio_input_dir
        identifier = ""

        if url:
            input_dir, identifier = self.download_audio(url, main_output_dir)
        elif output_dir:
            identifier = output_dir

        identifier = self.sanitize_filename(identifier, 50)

        if not input_dir or not os.path.isdir(input_dir):
            logging.error("No valid input directory provided.")
            return

        # Run processing steps
        wav_output_dir = os.path.join(main_output_dir, "wav_conversion")
        separation_output_dir = os.path.join(main_output_dir, "separation_output")
        slicing_output_dir = os.path.join(main_output_dir, "slicing_output")
        final_output_dir = os.path.join(main_output_dir, "final_output")
        os.makedirs(final_output_dir, exist_ok=True)

        self.wav_conversion(input_dir, wav_output_dir)
        self.separation(wav_output_dir, separation_output_dir)
        self.slicing(separation_output_dir, slicing_output_dir)
        self.transcribe(slicing_output_dir)

        # Locate the slicing output subdirectory
        slicing_output_subdir = None
        for subfolder in os.listdir(slicing_output_dir):
            subfolder_path = os.path.join(slicing_output_dir, subfolder)
            if os.path.isdir(subfolder_path):
                slicing_output_subdir = subfolder_path
                break

        if not slicing_output_subdir:
            logging.error("No subfolder found in slicing output for renaming and copying to final output.")
            return

        self.rename_and_copy_transcription_files(slicing_output_subdir, final_output_dir)
        zip_name = f"{self.get_oldest_file_date(input_dir)}-{identifier}" if identifier else self.get_oldest_file_date(input_dir)
        self.zip_final_output(final_output_dir, main_output_dir, zip_name)

        # Return the main output directory path for use in workflows
        return (main_output_dir,)

    # Functions from fapMixPlus.py
    def download_audio(self, url, download_dir):
        import yt_dlp
        temp_audio_file_path = os.path.join(download_dir, 'downloaded_audio.m4a')
        ydl_opts = {
            'format': '140',
            'outtmpl': temp_audio_file_path,
            'quiet': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(url, download=True)
                title = result.get('title', '')
        except Exception as e:
            logging.error(f"Error downloading audio: {e}")
            return None, None
        return download_dir, title

    def wav_conversion(self, input_dir, output_dir):
        self.run_command(['fap', 'to-wav', '--recursive', input_dir, output_dir], "WAV Conversion")

    def separation(self, input_dir, output_dir):
        self.run_command(['fap', 'separate', input_dir, output_dir], "Separation")

    def slicing(self, input_dir, output_dir):
        self.run_command(['fap', 'slice-audio-v2', '--no-merge-short', '--min-duration', '3', input_dir, output_dir], "Slicing")

    def transcribe(self, input_dir):
        self.run_command(['fap', 'transcribe', '--lang', 'en', '--recursive', input_dir], "Transcription")

    def rename_and_copy_transcription_files(self, slicing_output_subdir, final_output_dir):
        os.makedirs(final_output_dir, exist_ok=True)
        for i, file in enumerate(sorted(os.listdir(slicing_output_subdir))):
            if file.endswith(".wav"):
                lab_file_path = os.path.join(slicing_output_subdir, file.replace(".wav", ".lab"))
                prefix = f"{i:04d}"
                if os.path.exists(lab_file_path):
                    with open(lab_file_path, 'r') as lab_file:
                        transcription_text = lab_file.readline().strip()
                    words = "_".join(transcription_text.split()[:10]) if transcription_text else ""
                    dest_file_name = self.sanitize_filename(words, 128) if words else prefix
                    shutil.copy(os.path.join(slicing_output_subdir, file), os.path.join(final_output_dir, dest_file_name + ".wav"))
                    shutil.copy(lab_file_path, os.path.join(final_output_dir, dest_file_name + ".lab"))
                else:
                    logging.warning(f"Matching .lab file for {file} not found. Skipping.")

    def sanitize_filename(self, name, max_length=128):
        return "".join(char if char.isalnum() or char == "_" else "_" for char in name)[:max_length]

    def get_oldest_file_date(self, input_dir):
        files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        oldest_file = min(files, key=os.path.getmtime) if files else None
        return datetime.fromtimestamp(os.path.getmtime(oldest_file)).strftime("%d%B%Y") if oldest_file else ""

    def zip_final_output(self, final_output_dir, output_dir, zip_name):
        zip_path = os.path.join(output_dir, f"{zip_name}.zip")
        shutil.make_archive(zip_path.replace(".zip", ""), 'zip', final_output_dir)
        logging.info(f"Final output zipped as {zip_path}")

    def run_command(self, command, stage_name):
        logging.info(f"Running stage: {stage_name}")
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error during {stage_name} execution: {e}")
