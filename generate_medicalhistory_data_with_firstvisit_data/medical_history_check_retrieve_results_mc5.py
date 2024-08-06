import os
import json
from openai import OpenAI
import glob
from tqdm import tqdm

# Replace with your OpenAI API key
api_key = 'sk-proj-jC9e79Ot28S4DnIW1gfFT3BlbkFJusxyPFai8TjJBIZ6LPww'

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Base output directory
OUTPUT_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files_medhistory\output'

def load_log_entry(log_file):
    with open(log_file, 'r') as f:
        entries = [json.loads(line) for line in f]
    return entries[-1] if entries else None

def update_log(log_file, entry):
    with open(log_file, 'a') as f:
        json.dump(entry, f)
        f.write('\n')

def check_batch_status(batch_id):
    return client.batches.retrieve(batch_id)

def download_results(batch_id, output_dir, batch_prompt_filename):
    response = client.batches.retrieve(batch_id)
    result_file_id = response.output_file_id
    if result_file_id is None:
        raise ValueError("No output file available yet.")
    
    result_file = client.files.content(result_file_id)
    
    result_filename = f"results_{batch_prompt_filename}"
    result_file_path = os.path.join(output_dir, result_filename)
    with open(result_file_path, 'w') as f:
        f.write(result_file.text)
    
    return result_file_path, result_file_id

def calculate_cost(input_tokens, output_tokens):
    input_cost = input_tokens * 0.075 / 1000000  # $0.075 per 1M tokens for input
    output_cost = output_tokens * 0.300 / 1000000  # $0.300 per 1M tokens for output
    return input_cost + output_cost

def calculate_token_usage(result_file):
    total_input_tokens = 0
    total_output_tokens = 0
    try:
        with open(result_file, 'r') as f:
            for line in f:
                data = json.loads(line)
                usage = data['response']['body']['usage']
                total_input_tokens += usage['prompt_tokens']
                total_output_tokens += usage['completion_tokens']
    except Exception as e:
        print(f"Error calculating token usage: {str(e)}")
    return total_input_tokens, total_output_tokens

def process_job(log_file):
    log_entry = load_log_entry(log_file)
    if not log_entry:
        return None, None

    if log_entry['status'] in ['completed', 'failed']:
        return log_entry['status'], log_entry.get('result_file')

    try:
        batch_id = log_entry['batch_id']
        status_response = check_batch_status(batch_id)
        current_status = status_response.status

        if current_status in ['in_progress', 'finalizing']:
            log_entry['status'] = current_status
            return current_status, None
        elif current_status == 'failed':
            log_entry['status'] = current_status
            log_entry['error'] = "Job failed"
            return 'failed', None
        elif current_status == 'completed':
            batch_prompt_filename = os.path.basename(log_entry['input_file'])
            result_file, output_file_id = download_results(batch_id, log_entry['output_directory'], batch_prompt_filename)
            
            log_entry['status'] = current_status
            log_entry['result_file'] = result_file
            log_entry['output_file_id'] = output_file_id
            log_entry['result_filename'] = os.path.basename(result_file)
            return 'completed', result_file
        else:
            log_entry['status'] = current_status
            log_entry['error'] = f"Unknown status: {current_status}"
            return 'unknown', None

    except Exception as e:
        log_entry['status'] = 'error'
        log_entry['error'] = str(e)
        print(f"Error processing job {log_file}: {str(e)}")
        return 'error', None
    finally:
        update_log(log_file, log_entry)
def calculate_total_tokens_and_cost(all_log_files):
    total_input_tokens = 0
    total_output_tokens = 0
    for log_file in all_log_files:
        log_entry = load_log_entry(log_file)
        if log_entry and log_entry['status'] == 'completed':
            total_input_tokens += log_entry.get('input_tokens', 0)
            total_output_tokens += log_entry.get('output_tokens', 0)
    total_cost = calculate_cost(total_input_tokens, total_output_tokens)
    return total_input_tokens, total_output_tokens, total_cost

def main():
    all_log_files = [log_file for subdir in glob.glob(os.path.join(OUTPUT_DIR, 'sub_*')) 
                     for log_file in glob.glob(os.path.join(subdir, 'logs_*.jsonl'))]
    
    job_status = {'in_progress': 0, 'finalizing': 0, 'completed': 0, 'error': 0, 'failed': 0}
    newly_completed_jobs = 0
    new_input_tokens = 0
    new_output_tokens = 0
    
    with tqdm(total=len(all_log_files), desc="Processing jobs", unit="job") as pbar:
        for log_file in all_log_files:
            previous_status = load_log_entry(log_file)['status'] if load_log_entry(log_file) else None
            status, result_file = process_job(log_file)
            job_status[status] = job_status.get(status, 0) + 1
            
            if status == 'completed' and previous_status != 'completed':
                newly_completed_jobs += 1
                if result_file:
                    input_tokens, output_tokens = calculate_token_usage(result_file)
                    new_input_tokens += input_tokens
                    new_output_tokens += output_tokens
            pbar.update(1)

    new_cost = calculate_cost(new_input_tokens, new_output_tokens)
    total_input_tokens, total_output_tokens, total_cost = calculate_total_tokens_and_cost(all_log_files)

    print(f"\nJob Status Summary:")
    for status, count in job_status.items():
        print(f"{status.capitalize()}: {count}")
    
    print(f"\nNewly Completed Jobs in This Run: {newly_completed_jobs}")
    print(f"Total Input Tokens for Newly Completed Jobs: {new_input_tokens}")
    print(f"Total Output Tokens for Newly Completed Jobs: {new_output_tokens}")
    print(f"Total Cost for Newly Completed Jobs: ${new_cost:.6f}")

    print(f"\nTotal Input and Output Tokens for All Jobs: {total_input_tokens + total_output_tokens}")
    print(f"Total Cost for All Jobs: ${total_cost:.6f}")

if __name__ == "__main__":
    main()
