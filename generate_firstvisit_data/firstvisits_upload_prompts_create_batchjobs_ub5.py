# Shaswato Sarker - TrustedAI

import os
import json
import time
from datetime import datetime
from openai import OpenAI
import tkinter as tk
from tkinter import filedialog

# Replace with your OpenAI API key
api_key = 'sk-proj-jC9e79Ot28S4DnIW1gfFT3BlbkFJusxyPFai8TjJBIZ6LPww'

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Base directories
INPUT_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\input'
OUTPUT_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\output'

def select_files():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        initialdir=INPUT_DIR,
        filetypes=[("JSONL files", "*.jsonl")]
    )
    return file_paths

def create_output_directory(filename):
    base_name = os.path.splitext(os.path.basename(filename))[0]
    output_dir = os.path.join(OUTPUT_DIR, f"sub_{base_name}")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def create_log_entry(filename):
    return {
        "input_file": filename,
        "input_directory": INPUT_DIR,
        "upload_timestamp": datetime.now().isoformat(),
        "file_id": None,
        "openai_filename": None,
        "batch_id": None,
        "status": "uploading",
        "output_directory": None,
        "result_file": None,
        "error": None
    }

def update_log(log_file, entry):
    with open(log_file, 'a') as f:
        json.dump(entry, f)
        f.write('\n')

def upload_jsonl_file(file_path):
    with open(file_path, "rb") as file:
        response = client.files.create(file=file, purpose='batch')
    return response.id, response.filename

def create_batch_job(file_id):
    batch_response = client.batches.create(
        input_file_id=file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": "batch job"}
    )
    return batch_response.id, batch_response.status

def process_file(jsonl_file_path):
    base_name = os.path.splitext(os.path.basename(jsonl_file_path))[0]
    output_dir = create_output_directory(base_name)
    log_file = os.path.join(output_dir, f"logs_{base_name}.jsonl")

    # Check if file was already processed
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                if entry['input_file'] == jsonl_file_path and entry['status'] != 'failed':
                    print(f"File {jsonl_file_path} was already processed. Skipping.")
                    return

    log_entry = create_log_entry(jsonl_file_path)
    update_log(log_file, log_entry)

    try:
        # Upload JSONL file
        file_id, openai_filename = upload_jsonl_file(jsonl_file_path)
        log_entry.update({
            "file_id": file_id,
            "openai_filename": openai_filename,
            "status": "uploaded"
        })
        update_log(log_file, log_entry)

        # Create batch job
        batch_id, status = create_batch_job(file_id)
        log_entry.update({
            "batch_id": batch_id,
            "status": status,
            "output_directory": output_dir
        })
        update_log(log_file, log_entry)

        # Move input file to output directory
        new_input_file_path = os.path.join(output_dir, os.path.basename(jsonl_file_path))
        os.rename(jsonl_file_path, new_input_file_path)
        log_entry["input_directory"] = output_dir
        update_log(log_file, log_entry)

        print(f"Processed file: {jsonl_file_path}")
        print(f"Batch job created with ID: {batch_id}")
        print(f"Log file created: {log_file}")

    except Exception as e:
        log_entry.update({
            "status": "failed",
            "error": str(e)
        })
        update_log(log_file, log_entry)
        print(f"Error processing file {jsonl_file_path}: {str(e)}")

def main():
    jsonl_file_paths = select_files()
    if not jsonl_file_paths:
        print("No files selected. Exiting.")
        return

    for jsonl_file_path in jsonl_file_paths:
        print(f"\nProcessing file: {jsonl_file_path}")
        process_file(jsonl_file_path)

    print("\nAll files processed.")

if __name__ == "__main__":
    main()
