import os
import json
from openai import OpenAI
import glob
from datetime import datetime

# Replace with your OpenAI API key
api_key = 'sk-proj-jC9e79Ot28S4DnIW1gfFT3BlbkFJusxyPFai8TjJBIZ6LPww'

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Base output directory
OUTPUT_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\output'
UNIFIED_LOG_FILE = os.path.join(OUTPUT_DIR, 'unified_job_log.json')

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

def load_or_create_unified_log():
    if os.path.exists(UNIFIED_LOG_FILE):
        with open(UNIFIED_LOG_FILE, 'r') as f:
            log = json.load(f)
        # Ensure the log has the correct structure
        if 'jobs' not in log:
            log['jobs'] = {}
        if 'total_completed' not in log:
            log['total_completed'] = 0
        if 'total_downloaded' not in log:
            log['total_downloaded'] = 0
    else:
        log = {'jobs': {}, 'total_completed': 0, 'total_downloaded': 0}
    return log


def update_unified_log(unified_log, job_id, status, result_file=None, error=None):
    if job_id not in unified_log['jobs']:
        unified_log['jobs'][job_id] = {'previous_status': None}
    
    job = unified_log['jobs'][job_id]
    job['status'] = status
    job['last_checked'] = datetime.now().isoformat()
    
    if result_file:
        job['result_file'] = result_file
        if job['previous_status'] != 'completed':
            unified_log['total_downloaded'] += 1
    
    if error:
        job['error'] = error
    
    if status == 'completed' and job['previous_status'] != 'completed':
        unified_log['total_completed'] += 1
    
    job['previous_status'] = status
    
    with open(UNIFIED_LOG_FILE, 'w') as f:
        json.dump(unified_log, f, indent=2)


def process_job(log_file, unified_log):
    log_entry = load_log_entry(log_file)
    if not log_entry:
        return None, None, False, False

    job_id = os.path.basename(log_file)
    previous_status = unified_log['jobs'].get(job_id, {}).get('status')
    
    if log_entry['status'] in ['completed', 'failed']:
        update_unified_log(unified_log, job_id, log_entry['status'], log_entry.get('result_file'), log_entry.get('error'))
        return log_entry['status'], log_entry.get('result_file'), False, False

    try:
        batch_id = log_entry['batch_id']
        status_response = check_batch_status(batch_id)
        current_status = status_response.status

        if current_status in ['in_progress', 'finalizing']:
            log_entry['status'] = current_status
            update_unified_log(unified_log, job_id, current_status)
            return current_status, None, False, False
        elif current_status == 'failed':
            log_entry['status'] = current_status
            log_entry['error'] = "Job failed"
            update_unified_log(unified_log, job_id, current_status, error="Job failed")
            return 'failed', None, False, False
        elif current_status == 'completed':
            batch_prompt_filename = os.path.basename(log_entry['input_file'])
            result_file, output_file_id = download_results(batch_id, log_entry['output_directory'], batch_prompt_filename)
            log_entry['status'] = current_status
            log_entry['result_file'] = result_file
            log_entry['output_file_id'] = output_file_id
            log_entry['result_filename'] = os.path.basename(result_file)
            update_unified_log(unified_log, job_id, current_status, result_file)
            return 'completed', result_file, previous_status != 'completed', previous_status != 'completed'
        else:
            log_entry['status'] = current_status
            log_entry['error'] = f"Unknown status: {current_status}"
            update_unified_log(unified_log, job_id, current_status, error=f"Unknown status: {current_status}")
            return 'unknown', None, False, False

    except Exception as e:
        log_entry['status'] = 'error'
        log_entry['error'] = str(e)
        update_unified_log(unified_log, job_id, 'error', error=str(e))
        return 'error', None, False, False
    finally:
        update_log(log_file, log_entry)

def main():
    unified_log = load_or_create_unified_log()
    completed_jobs_this_run = 0
    results_downloaded_this_run = 0
    in_progress_jobs = 0
    finalizing_jobs = 0
    failed_jobs = 0
    
    for subdir in glob.glob(os.path.join(OUTPUT_DIR, 'sub_*')):
        log_files = glob.glob(os.path.join(subdir, 'logs_*.jsonl'))
        for log_file in log_files:
            status, result_file, completed_this_run, downloaded_this_run = process_job(log_file, unified_log)
            
            if status == 'completed':
                if completed_this_run:
                    completed_jobs_this_run += 1
                if downloaded_this_run:
                    results_downloaded_this_run += 1
            elif status == 'in_progress':
                in_progress_jobs += 1
            elif status == 'finalizing':
                finalizing_jobs += 1
            elif status in ['failed', 'error']:
                failed_jobs += 1

    print(f"\nSummary:")
    print(f"Jobs completed in this run: {completed_jobs_this_run}")
    print(f"Results downloaded in this run: {results_downloaded_this_run}")
    print(f"Jobs still in progress: {in_progress_jobs}")
    print(f"Jobs finalizing: {finalizing_jobs}")
    print(f"Jobs failed or errored: {failed_jobs}")
    print(f"\nTotal Statistics:")
    print(f"Total Jobs Completed: {unified_log['total_completed']}")
    print(f"Total Results Downloaded: {unified_log['total_downloaded']}")

if __name__ == "__main__":
    main()


