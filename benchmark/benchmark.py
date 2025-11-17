#!/usr/bin/env python3
"""
Benchmark script for ASR-API
Runs multiple transcription requests against the API and measures performance.
"""

import argparse
import time
import statistics
from pathlib import Path
from typing import List, Dict
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


def transcribe_file(api_url: str, file_path: Path, run_id: int) -> Dict:
    """Send a transcription request to the API."""
    start_time = time.time()
    
    try:
        with open(file_path, 'rb') as f:
            files = {'audio_file': (file_path.name, f, 'audio/wav')}
            data = {
                'encode': True,
                'task': 'transcribe',
                'output': 'json'
            }
            
            response = requests.post(
                f"{api_url}/asr",
                files=files,
                data=data,
                timeout=300  # 5 minute timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                return {
                    'run_id': run_id,
                    'file': file_path.name,
                    'success': True,
                    'duration': duration,
                    'status_code': response.status_code,
                    'response_size': len(response.content)
                }
            else:
                return {
                    'run_id': run_id,
                    'file': file_path.name,
                    'success': False,
                    'duration': duration,
                    'status_code': response.status_code,
                    'error': response.text[:100]
                }
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        return {
            'run_id': run_id,
            'file': file_path.name,
            'success': False,
            'duration': duration,
            'error': str(e)
        }


def run_benchmark(api_url: str, data_dir: Path, num_runs: int, concurrent: int = 1):
    """Run benchmark with specified number of runs."""
    # Get all audio files from data directory
    audio_files = list(data_dir.glob('*.wav')) + list(data_dir.glob('*.mp3')) + list(data_dir.glob('*.m4a'))
    
    if not audio_files:
        print(f"❌ No audio files found in {data_dir}")
        return
    
    print(f"📁 Found {len(audio_files)} audio file(s) in {data_dir}")
    print(f"🔄 Running {num_runs} transcription(s)...")
    print(f"🌐 API URL: {api_url}")
    print(f"⚡ Concurrent requests: {concurrent}")
    print("-" * 60)
    
    results: List[Dict] = []
    start_time = time.time()
    
    # Prepare all runs
    runs = []
    for i in range(num_runs):
        file_path = audio_files[i % len(audio_files)]  # Cycle through files
        runs.append((file_path, i + 1))
    
    # Execute runs
    if concurrent == 1:
        # Sequential execution
        for file_path, run_id in runs:
            result = transcribe_file(api_url, file_path, run_id)
            results.append(result)
            status = "✅" if result['success'] else "❌"
            print(f"{status} Run {run_id}/{num_runs}: {result['file']} - {result['duration']:.2f}s")
    else:
        # Concurrent execution
        with ThreadPoolExecutor(max_workers=concurrent) as executor:
            future_to_run = {
                executor.submit(transcribe_file, api_url, file_path, run_id): (file_path, run_id)
                for file_path, run_id in runs
            }
            
            for future in as_completed(future_to_run):
                result = future.result()
                results.append(result)
                status = "✅" if result['success'] else "❌"
                print(f"{status} Run {result['run_id']}/{num_runs}: {result['file']} - {result['duration']:.2f}s")
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    successful_runs = [r for r in results if r['success']]
    failed_runs = [r for r in results if not r['success']]
    
    if successful_runs:
        durations = [r['duration'] for r in successful_runs]
        avg_duration = statistics.mean(durations)
        median_duration = statistics.median(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        if len(durations) > 1:
            stdev_duration = statistics.stdev(durations)
        else:
            stdev_duration = 0
        
        # Calculate percentiles
        sorted_durations = sorted(durations)
        p50 = sorted_durations[int(len(sorted_durations) * 0.50)]
        p95 = sorted_durations[int(len(sorted_durations) * 0.95)] if len(sorted_durations) > 1 else sorted_durations[0]
        p99 = sorted_durations[int(len(sorted_durations) * 0.99)] if len(sorted_durations) > 1 else sorted_durations[0]
    else:
        avg_duration = median_duration = min_duration = max_duration = stdev_duration = 0
        p50 = p95 = p99 = 0
    
    # Print summary
    print("-" * 60)
    print("📊 BENCHMARK SUMMARY")
    print("-" * 60)
    print(f"Total runs: {num_runs}")
    print(f"Successful: {len(successful_runs)}")
    print(f"Failed: {len(failed_runs)}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Throughput: {len(successful_runs) / total_time:.2f} requests/sec")
    print()
    print("⏱️  LATENCY STATISTICS (successful requests)")
    print(f"  Average: {avg_duration:.2f}s")
    print(f"  Median:  {median_duration:.2f}s")
    print(f"  Min:     {min_duration:.2f}s")
    print(f"  Max:     {max_duration:.2f}s")
    print(f"  StdDev:  {stdev_duration:.2f}s")
    print(f"  P50:     {p50:.2f}s")
    print(f"  P95:     {p95:.2f}s")
    print(f"  P99:     {p99:.2f}s")
    
    if failed_runs:
        print()
        print("❌ FAILED REQUESTS:")
        for run in failed_runs:
            print(f"  Run {run['run_id']}: {run.get('error', 'Unknown error')}")


def main():
    parser = argparse.ArgumentParser(description='Benchmark ASR-API performance')
    parser.add_argument(
        '--number-of-runs',
        type=int,
        default=10,
        help='Number of transcription runs to execute (default: 10)'
    )
    parser.add_argument(
        '--api-url',
        type=str,
        default='http://asr.api.k25.local',
        help='ASR-API URL (default: http://asr.api.k25.local)'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='Directory containing audio files (default: data)'
    )
    parser.add_argument(
        '--concurrent',
        type=int,
        default=1,
        help='Number of concurrent requests (default: 1)'
    )
    
    args = parser.parse_args()
    
    # Resolve data directory path
    script_dir = Path(__file__).parent
    data_dir = script_dir / args.data_dir
    
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    run_benchmark(args.api_url, data_dir, args.number_of_runs, args.concurrent)


if __name__ == '__main__':
    main()

