import os

from dotenv import load_dotenv

from logging_config import logger

load_dotenv()

class Config:
    def __init__(self):
        try:
            self.elasticsearch_host = os.getenv('ELASTIC_TARGET')
            self.elasticsearch_username = os.getenv('ELASTIC_USER')
            self.elasticsearch_password = os.getenv('ELASTIC_PASS')
            self.repository_name = os.getenv('ELASTIC_REPOSITORY_NAME')
            self.min_days_to_snapshot = os.getenv('ELASTIC_MIN_DAYS_TO_SNAPSHOT')
            self.data_stream_pattern = os.getenv('ELASTIC_DATA_STREAM_PATTERN')
            self.delete_data_stream_after_snapshot = os.getenv('ELASTIC_DELETE_DATA_STREAM_AFTER_SNAPSHOT', 'false').lower() == 'true'
            self.delete_old_snapshots = os.getenv('ELASTIC_DELETE_OLD_SNAPSHOTS', 'false').lower() == 'true'
            self.min_days_to_delete_snapshot = os.getenv('ELASTIC_MIN_DAYS_TO_DELETE_SNAPSHOT')
            self.max_workers = os.getenv('MAX_WORKERS', '4')

            self._validate()
        except Exception as e:
            logger.error(f"Error initializing config: {e}")
            raise
    
    def _validate(self):
        """Validates the configuration settings"""
        required_vars = {
            'ELASTIC_TARGET': self.elasticsearch_host,
            'ELASTIC_USER': self.elasticsearch_username,
            'ELASTIC_PASS': self.elasticsearch_password,
            'ELASTIC_REPOSITORY_NAME': self.repository_name,
            'ELASTIC_DATA_STREAM_PATTERN': self.data_stream_pattern,
            'ELASTIC_MIN_DAYS_TO_SNAPSHOT': self.min_days_to_snapshot
        }
        
        if self.delete_old_snapshots:
            required_vars['ELASTIC_MIN_DAYS_TO_DELETE_SNAPSHOT'] = self.min_days_to_delete_snapshot
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        try:
            self.min_days_to_snapshot = int(self.min_days_to_snapshot)
        except ValueError:
            raise ValueError("ELASTIC_MIN_DAYS_TO_SNAPSHOT must be an integer")

        if self.delete_old_snapshots:
            try:
                self.min_days_to_delete_snapshot = int(self.min_days_to_delete_snapshot)
            except ValueError:
                raise ValueError("ELASTIC_MIN_DAYS_TO_DELETE_SNAPSHOT must be an integer")

        try:
            self.max_workers = int(self.max_workers)
        except ValueError:
            raise ValueError("MAX_WORKERS must be an integer")
