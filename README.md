# preFapMix.py

**preFapMix.py** is an audio processing script that applies soft limiting, optional loudness normalization, and optional slicing for transcription. It can also produce stereo-mixed outputs with optional audio appended to the end. The script organizes processed files into structured folders with sanitized filenames and retains original timestamps for continuity.

## Features

1. **Soft Limiting**: Reduces loud peaks in audio to prevent clipping.
2. **Optional Loudness Normalization**: Adjusts audio levels to achieve consistent loudness.
3. **Conditional Slicing and Transcription**: Options to slice and transcribe files in the left or right channels separately, or both channels together.
4. **Stereo Mixing with Optional Tone Appending**: Optionally appends a custom tone (`tones.wav`) to the end of stereo-mixed audio.
5. **Organized Output Structure**: Outputs are saved in structured folders with sanitized filenames.
6. **Timestamp Preservation**: Maintains the original timestamps for all output files.

## Installation Requirements

- **Python 3.x**
- **Pydub** for audio processing
  ```bash
  pip install pydub
  ```
- **FFmpeg**: Required by Pydub for handling audio files
  ```bash
  sudo apt-get install ffmpeg
  ```
- **fap**: The transcription tool, assumed to be installed and accessible via the command line.

## Usage

### Command Line

Run the script from the command line with the following arguments:

```bash
python preFapMix.py --input-dir <input_directory> --output-dir <output_directory> [options]
```

### Options

- **`--input-dir`**: Directory containing input audio files (required).
- **`--output-dir`**: Directory where processed files will be saved (required).
- **`--transcribe`**: Enables transcription for both left and right channels. Implies both `--transcribe_left` and `--transcribe_right`.
- **`--transcribe_left`**: Enables transcription only for the left channel.
- **`--transcribe_right`**: Enables transcription only for the right channel.
- **`--normalize`**: Enables loudness normalization on the audio.
- **`--tones`**: Appends the contents of `tones.wav` to the end of each stereo output file.
- **`--num-workers`**: Specifies the number of workers to use for transcription (default is 2).

### Workflow

1. **Pre-Processing**:
   - Applies a soft limiter at -6 dB to control peaks.
   - If `--normalize` is enabled, normalizes loudness to -23 LUFS for consistency.

2. **Conditional Slicing and Transcription**:
   - If `--transcribe` is enabled, slices audio files to smaller segments and transcribes each segment, generating `.lab` files.
   - With `--transcribe_left` or `--transcribe_right`, transcribes only files in the left or right folders, respectively.

3. **Stereo Mixing with Optional Tone Appending**:
   - Combines left and right channels into a stereo file.
   - If `--tones` is enabled, appends `tones.wav` to the end of each stereo file.

4. **File Naming and Organization**:
   - Names each sliced audio file with its original numeric name, followed by the first 12 words (or fewer) from its `.lab` file.
   - All filenames are sanitized for UTF-8 compliance.

### Output Structure

The output structure is organized within `<output_directory>/run_<timestamp>` as follows:

- **`normalized/`**: Contains normalized versions of the input audio files.
- **`left/`** and **`right/`**: Contains sliced (and optionally transcribed) audio files in respective left and right channel folders.
- **`stereo/`**: Contains stereo-mixed files with optional tone appended to the end.
- **`transcribed-and-sliced/`**:
  - Root: Contains combined `.lab` files for each original input.
  - **`left/`** and **`right/`**: Contains subfolders of sliced audio files and corresponding `.lab` files.

### Example Command

```bash
python preFapMix.py --input-dir ./my_audio_files --output-dir ./processed_audio --transcribe --normalize --tones --num-workers 3
```

This command will:
1. Process the audio files in `./my_audio_files` with soft limiting and loudness normalization.
2. Slice and transcribe each file in the left and right channels.
3. Mix each pair of left and right channels into a stereo file and append `tones.wav` to the end of each stereo output.

# fapMixPlus

This project provides an end-to-end audio processing pipeline to automate the extraction, separation, slicing, transcription, and renaming of audio files. The resulting files are saved in a structured output directory with cleaned filenames and optional ZIP archives for easier distribution or storage.

## Features

- **Download Audio**: Fetches audio files from a URL or uses local input files.
- **Convert to WAV**: Converts audio files to WAV format.
- **Separate Vocals**: Isolates vocal tracks from the WAV files.
- **Slice Audio**: Segments the separated vocal track for transcription.
- **Transcribe**: Generates transcriptions from audio slices.
- **Sanitize and Rename Files**: Creates sanitized filenames with a numerical prefix, limited to 128 characters.
- **Generate ZIP Files**: Compresses processed files into ZIP archives for easy storage and distribution.

## Prerequisites

- **Python 3.x**
- Install required Python packages:
  ```bash
  pip install yt-dlp
  ```
- **Fish Audio Preprocessor (`fap`)** should be installed and available in the PATH.

### Installing the Fish Audio Preprocessor (`fap`)

1. Clone the [Fish Audio Preprocessor repository](https://github.com/fishaudio/audio-preprocess):
   ```bash
   git clone https://github.com/fishaudio/audio-preprocess.git
   ```

2. Navigate to the repository directory:
   ```bash
   cd audio-preprocess
   ```

3. Install the package from the cloned repository:
   ```bash
   pip install -e .
   ```

This step installs `fap` and makes it accessible as a command-line tool, which is essential for `fapMixPlus.py` to function correctly.

4. Verify the installation by checking the version:
   ```bash
   fap --version
   ```

## Usage

### Command-line Arguments

| Argument        | Description                                                          |
|-----------------|----------------------------------------------------------------------|
| `--url`         | URL of the audio source (YouTube or other supported link).           |
| `--output_dir`  | Directory for saving all outputs. Default is `output/`.              |
| `input_dir`     | Path to a local directory of input files (optional if `--url` used). |

### Example Command

```bash
python fapMixPlus.py --url https://youtu.be/example_video --output_dir my_output
```

This command will download the audio from the URL, process it, and save the results in the `my_output` folder.

### Output Structure

The output directory will contain a timestamped folder with the following structure:

```
output_<timestamp>/
├── wav_conversion/            # WAV-converted audio files
├── separation_output/         # Separated vocal track files
├── slicing_output/            # Sliced segments from separated audio
├── final_output/              # Final, sanitized, and renamed .wav and .lab files
├── zip_files/                 # Compressed ZIP archives of processed files
```

### ZIP File Details

In addition to organizing output files by processing stages, `fapMixPlus` can generate ZIP archives for convenience. Each ZIP file in the `zip_files/` directory will contain a set of processed audio and transcription files, with names based on their content and timestamp. The ZIP filenames will follow this format:

```
output_<timestamp>.zip
```

Each ZIP file will include:
- The WAV and `.lab` files from `final_output/`, with sanitized filenames.
- These ZIP files are ideal for transferring or archiving processed audio.

## Functionality Details

1. **Download Audio**: Downloads audio from a URL, saving it in `.m4a` format.
2. **WAV Conversion**: Converts audio to WAV using `fap to-wav`.
3. **Separation**: Separates vocals from the WAV files using `fap separate`.
4. **Slicing**: Segments the separated vocal track into smaller audio slices.
5. **Transcription**: Uses `fap transcribe` to transcribe each slice.
6. **Sanitization and Renaming**:
   - Extracts the first 10 words from each `.lab` file.
   - Replaces spaces with underscores, removes special characters, and limits to 128 characters.
   - Applies a numerical prefix if no valid content is in the `.lab` file.
7. **ZIP File Creation**:
   - After processing, the final `.wav` and `.lab` files are compressed into ZIP archives in `zip_files/` for each session, making it easy to organize or share the output.

## Example File Names in Final Output

Final output files in `final_output` will be structured like:
- `0001_Hello_this_is_a_sample_transcription.wav`
- `0001_Hello_this_is_a_sample_transcription.lab`

Files without usable `.lab` content will retain the numerical prefix, e.g., `0002.wav` and `0002.lab`.