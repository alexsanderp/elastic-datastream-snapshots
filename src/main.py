import argparse
import concurrent.futures
import warnings
from typing import List

from elastic_transport import SecurityWarning
from urllib3.exceptions import InsecureRequestWarning

from logging_config import logger
from snapshot_operations import SnapshotOperations

warnings.simplefilter('ignore', SecurityWarning)
warnings.simplefilter('ignore', InsecureRequestWarning)

snapshot_ops = SnapshotOperations()

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Elasticsearch Snapshot Manager')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry run mode (no changes will be made)')
    return parser.parse_args()

def process_data_stream(data_stream: str, dry_run: bool = False) -> None:
    """
    Processes a single data stream (create snapshot and delete if necessary).
    
    Args:
        data_stream (str): Name of the data stream to process.
        dry_run (bool): If True, only simulate the operation.
    """
    should_skip, reason = snapshot_ops.snapshot_exists(data_stream)
    if should_skip:
        logger.warning(f"Skipping {data_stream} - {reason}")
        return
        
    if snapshot_ops.create_snapshot(data_stream, dry_run):
        if snapshot_ops.config.delete_data_stream_after_snapshot:
            snapshot_ops.delete_data_stream(data_stream, dry_run)

def process_data_streams(data_streams: List[str], dry_run: bool = False) -> None:
    """
    Processes all old data streams in parallel using thread pool.
    Continues processing even if some threads fail.
    
    Args:
        data_streams (List[str]): List of data streams to process.
        dry_run (bool): If True, only simulate the operation.
    """
    if not data_streams:
        logger.info("No data streams to process")
        return
    
    max_workers = snapshot_ops.config.max_workers
    logger.info(f"Processing {len(data_streams)} data streams with {max_workers} workers")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_data_stream, data_stream, dry_run)
            for data_stream in data_streams
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error processing data stream: {str(e)}")
                continue

def main():
    try:
        logger.info("Starting elasticsearch snapshots")
        args = parse_args()
        if args.dry_run:
            logger.info("Running in DRY RUN mode - no changes will be made")
        
        old_data_streams = snapshot_ops.get_data_streams_older_than_days()
        process_data_streams(old_data_streams, dry_run=args.dry_run)
        
        if snapshot_ops.config.delete_old_snapshots:
            snapshot_ops.delete_old_snapshots(dry_run=args.dry_run)
        
        logger.info("Finishing elasticsearch snapshots")
        
    except Exception as e:
        logger.error(str(e))
        raise

if __name__ == "__main__":
    main()  # pragma: no cover
