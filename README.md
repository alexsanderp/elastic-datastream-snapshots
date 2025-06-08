# Elastic Datastream Snapshots

A tool to manage Elastic snapshots and data streams, which creates snapshots, and optionally deletes data streams and old snapshots according to configurable rules.

> **Tested with Elasticsearch version 9.0.0**

## ✨ Features

- Creates one snapshot per data stream, which simplifies restoring specific data streams individually.
- Optionally deletes old snapshots.
- Optionally deletes data streams after successful snapshots.
- Supports dry-run mode to simulate operations.
- Parallel execution configurable via environment variable.

## 🚀 How It Works

1. Identifies all data streams matching a defined pattern.
2. Checks the age of each data stream.
3. If a data stream is older than ELASTIC_MIN_DAYS_TO_SNAPSHOT days:
   - A snapshot is created using the data stream name.
   - If ELASTIC_DELETE_DATA_STREAM_AFTER_SNAPSHOT=true, the data stream is deleted after the snapshot.
4. If ELASTIC_DELETE_OLD_SNAPSHOTS=true, snapshots older than ELASTIC_MIN_DAYS_TO_DELETE_SNAPSHOT days are deleted.

## 📦 Requirements

- Python >= 3.12.
- Elasticsearch 9.0.0 (or compatible).

## ⚙️ Environment Variables

| Variable                                    | Description                                                                | Required                                     |
|---------------------------------------------|----------------------------------------------------------------------------|----------------------------------------------|
| `ELASTIC_TARGET`                            | URL of your Elasticsearch instance (e.g. `https://elastic.example.com`)    | Yes                                          |
| `ELASTIC_USER`                              | Username for Elasticsearch authentication                                  | Yes                                          |
| `ELASTIC_PASS`                              | Password for Elasticsearch authentication                                  | Yes                                          |
| `ELASTIC_REPOSITORY_NAME`                   | Name of the snapshot repository                                            | Yes                                          |
| `ELASTIC_DATA_STREAM_PATTERN`               | Pattern used to match data streams (e.g. `logs-*`)                         | Yes                                          |
| `ELASTIC_MIN_DAYS_TO_SNAPSHOT`              | Minimum age (in days) of data streams to create a snapshot                 | Yes                                          |
| `ELASTIC_DELETE_OLD_SNAPSHOTS`              | Enable deletion of old snapshots (default: false)                          | No                                           |
| `ELASTIC_MIN_DAYS_TO_DELETE_SNAPSHOT`       | Minimum age (in days) of snapshots to be deleted                           | Yes (if `ELASTIC_DELETE_OLD_SNAPSHOTS=true`) |
| `ELASTIC_DELETE_DATA_STREAM_AFTER_SNAPSHOT` | Delete the data stream after a successful snapshot (default: false)        | No                                           |
| `MAX_WORKERS`                               | Number of parallel workers for snapshot and delete operations (default: 4) | No                                           |

## 📁 Example `.env`

```env
ELASTIC_TARGET=https://elastic.example.com
ELASTIC_USER=elastic
ELASTIC_PASS=your-secure-password
ELASTIC_REPOSITORY_NAME=your-elastic-repository-name
ELASTIC_DATA_STREAM_PATTERN=logs-*
ELASTIC_DELETE_DATA_STREAM_AFTER_SNAPSHOT=false
ELASTIC_MIN_DAYS_TO_SNAPSHOT=14
ELASTIC_DELETE_OLD_SNAPSHOTS=false
ELASTIC_MIN_DAYS_TO_DELETE_SNAPSHOT=30
MAX_WORKERS=4
```

### 🧪 Running Locally

```bash
git clone https://github.com/alexsanderp/elastic-datastream-snapshots.git
cd elastic-datastream-snapshots
cd src
pip install -r requirements.txt
cp .env.example .env   # Fill in your environment details
python main.py
```

To simulate the operations without making actual changes (dry run mode):

```bash
python main.py --dry-run
```

### 🐳 Running with Docker

```bash
docker pull alexsanderp/elastic-datastream-snapshots:latest
docker run --rm --env-file .env alexsanderp/elastic-datastream-snapshots:latest
```

## ✅ Testing

To run the tests:

```bash
cd src
pip install -r requirements-test.txt
pytest
```

## 🔐 Safety

- In **dry-run mode**, no snapshots or data streams are created, deleted, or modified.  
- The options `ELASTIC_DELETE_OLD_SNAPSHOTS` and `ELASTIC_DELETE_DATA_STREAM_AFTER_SNAPSHOT` are **disabled by default**, ensuring safety by avoiding unintended deletions.

## 🤝 Contributing

Contributions are welcome! Please open issues or submit pull requests for new features, bug fixes, or improvements. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 📬 Contact

For questions or feedback, feel free to open an issue on GitHub.
