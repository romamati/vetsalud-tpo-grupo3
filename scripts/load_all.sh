#!/usr/bin/env bash
set -euo pipefail

python -m mongodb_db.load_data
python -m neo4j_db.load_data
