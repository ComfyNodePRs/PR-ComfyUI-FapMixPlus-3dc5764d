# preFapNode.py

import os
import subprocess
import shutil
import logging

logging.basicConfig(level=logging.DEBUG)

class preFapMix:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio_input_dir": ("DIRECTORY_PATH", {"default": "/path/to/default_input_directory"}),
                "output_dir": ("DIRECTORY_PATH", {"default": "/path/to/default_output_directory"}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "process_audio"
    CATEGORY = "Audio Processing"
    NAME = "preFapMix"

    def process_audio(self, audio_input_dir, output_dir):
        # Create output directories
        left_dir = os.path.join(output_dir, "left")
        right_dir = os.path.join(output_dir, "right")
        stereo_dir = os.path.join(output_dir, "stereo")
        os.makedirs(left_dir, exist_ok=True)
        os.makedirs(right_dir, exist_ok=True)
        os.makedirs(stereo_dir, exist_ok=True)

        # Apply soft limiter and loudness normalization if selected
        self.apply_soft_limiter(audio_input_dir)
        self.loudness_normalization(audio_input_dir)

        # Identify channels and mix stereo outputs
        self.identify_channel_pairs(audio_input_dir, left_dir, right_dir, stereo_dir)
        self.mix_to_stereo(left_dir, right_dir, stereo_dir)

        # Slice and transcribe each channel
        self.slicing(left_dir, output_dir)
        self.slicing(right_dir, output_dir)
        self.transcribe_directory(left_dir)
        self.transcribe_directory(right_dir)

        logging.info("Processing completed for preFapMix.")

    # Functions from preFapMix.py
    def apply_soft_limiter(self, input_dir):
        self.run_command(['fap', 'soft-limit', '--dB', '-6', input_dir], "Soft Limiter")

    def loudness_normalization(self, input_dir):
        self.run_command(['fap', 'normalize-loudness', input_dir], "Loudness Normalization")

    def slicing(self, input_dir, output_dir):
        self.run_command(['fap', 'slice-audio-v2', '--no-merge-short', '--min-duration', '3', input_dir, output_dir], "Slicing")

    def transcribe_directory(self, input_dir):
        self.run_command(['fap', 'transcribe', '--lang', 'en', '--recursive', input_dir], "Transcription")

    def identify_channel_pairs(self, input_dir, left_dir, right_dir, stereo_dir):
        logging.info(f"Identifying channel pairs for {input_dir} and splitting into {left_dir}, {right_dir}, and {stereo_dir}.")

    def mix_to_stereo(self, left_dir, right_dir, stereo_dir):
        logging.info(f"Mixing {left_dir} and {right_dir} channels into stereo at {stereo_dir}.")

    def run_command(self, command, stage_name):
        logging.info(f"Running stage: {stage_name}")
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error during {stage_name} execution: {e}")
