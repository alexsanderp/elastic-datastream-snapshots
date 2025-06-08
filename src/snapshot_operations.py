from datetime import datetime, timedelta
from typing import List

from elasticsearch import Elasticsearch, NotFoundError

from config import Config
from logging_config import logger


class SnapshotError(Exception):
    """Base exception for snapshot operations"""
    pass


class SnapshotOperations:
    def __init__(self, config=None):
        self.config = config or Config()
        self.client = Elasticsearch(
            hosts=self.config.elasticsearch_host,
            basic_auth=(self.config.elasticsearch_username, self.config.elasticsearch_password),
            verify_certs=False
        )

    def get_data_streams_older_than_days(self) -> List[str]:
        """
        Gets all data streams older than the configured minimum days.
        
        Returns:
            List[str]: List of old data stream names.
            
        Raises:
            SnapshotError: If there's an error getting data streams from Elasticsearch.
        """
        try:
            data_streams = self.client.indices.get_data_stream(name=self.config.data_stream_pattern)
            data_streams = [stream['name'] for stream in data_streams['data_streams']]
            
            cutoff_date = datetime.now() - timedelta(days=self.config.min_days_to_snapshot)
            old_data_streams = []
            
            for stream in data_streams:
                try:
                    date_str = stream.split('-')[-1]
                    index_date = datetime.strptime(date_str, '%Y.%m.%d')
                    if index_date < cutoff_date:
                        old_data_streams.append(stream)
                except (ValueError, IndexError):
                    logger.warning(f"Could not parse date from data stream name: {stream}")
                    continue
            
            return old_data_streams
        except Exception as e:
            raise SnapshotError(f"Error getting data streams: {str(e)}")

    def snapshot_exists(self, data_stream_name: str) -> tuple[bool, str]:
        """
        Checks if a snapshot with the same name as the data stream already exists.
        If there's an error checking, returns True to skip the data stream.
        
        Args:
            data_stream_name (str): Name of the data stream to check.
            
        Returns:
            tuple[bool, str]: (True, reason) if should skip, (False, "") if should process
        """
        try:
            self.client.snapshot.get(
                repository=self.config.repository_name,
                snapshot=data_stream_name
            )
            return True, "snapshot already exists"
        except NotFoundError:
            return False, ""
        except Exception as e:
            return True, "could not verify snapshot existence"

    def create_snapshot(self, data_stream_name: str, dry_run: bool = False) -> bool:
        """
        Creates a snapshot for the specified data stream.
        
        Args:
            data_stream_name (str): Name of the data stream.
            dry_run (bool): If True, only simulates the operation without making changes.
            
        Returns:
            bool: True if the snapshot was created successfully, False otherwise.
        """
        if dry_run:
            logger.info(f"[DRY RUN] Would create snapshot for {data_stream_name}")
            return True
            
        try:
            self.client.snapshot.create(
                repository=self.config.repository_name,
                snapshot=data_stream_name,
                indices=data_stream_name,
                ignore_unavailable=False,
                include_global_state=False,
                partial=False,
                wait_for_completion=True
            )

            logger.info(f"Created snapshot: {data_stream_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating snapshot for {data_stream_name}: {str(e)}")
            return False

    def delete_data_stream(self, data_stream_name: str, dry_run: bool = False) -> bool:
        """
        Deletes a data stream.
        
        Args:
            data_stream_name (str): Name of the data stream.
            dry_run (bool): If True, only simulates the operation without making changes.
            
        Returns:
            bool: True if the data stream was deleted successfully, False otherwise.
        """
        if dry_run:
            logger.info(f"[DRY RUN] Would delete data stream {data_stream_name}")
            return True
            
        try:
            self.client.indices.delete_data_stream(name=data_stream_name)
            logger.info(f"Deleted data stream: {data_stream_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting data stream {data_stream_name}: {str(e)}")
            return False

    def delete_old_snapshots(self, dry_run: bool = False) -> bool:
        """
        Deletes snapshots older than the configured minimum days.
        Only considers snapshots that match the configured data stream pattern.
        
        Args:
            dry_run (bool): If True, only simulates the operation without making changes.
            
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            snapshots = self.client.snapshot.get(
                repository=self.config.repository_name,
                snapshot=self.config.data_stream_pattern
            )
            
            cutoff_date = datetime.now() - timedelta(days=self.config.min_days_to_delete_snapshot)
            deleted_count = 0
            
            for snapshot in snapshots['snapshots']:
                try:
                    date_str = snapshot['snapshot'].split('-')[-1]
                    snapshot_date = datetime.strptime(date_str, '%Y.%m.%d')
                    
                    if snapshot_date < cutoff_date:
                        if dry_run:
                            logger.info(f"[DRY RUN] Would delete old snapshot: {snapshot['snapshot']}")
                            deleted_count += 1
                        else:
                            self.client.snapshot.delete(
                                repository=self.config.repository_name,
                                snapshot=snapshot['snapshot']
                            )
                            logger.info(f"Deleted old snapshot: {snapshot['snapshot']}")
                            deleted_count += 1
                except (ValueError, IndexError):
                    logger.warning(f"Could not parse date from snapshot name: {snapshot['snapshot']}")
                    continue
            
            if deleted_count == 0:
                logger.info("No old snapshots to delete")
            elif dry_run:
                logger.info(f"[DRY RUN] Would delete {deleted_count} old snapshots")
            else:
                logger.info(f"Successfully deleted {deleted_count} old snapshots")
            
            return True
        except Exception as e:
            logger.error(f"Error deleting old snapshots: {str(e)}")
            return False
