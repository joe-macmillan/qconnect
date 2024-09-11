import json
import os
import time
from enum import Enum
from pathlib import Path

class CacheType(str, Enum):
    CLUSTER = 'cluster'
    SUBSCRIPTION = 'subs'

DATA_FOLDER = Path.home() / '.qc/'
CLUSTER_CACHE_FILE = DATA_FOLDER / "clusters.json"
SUBSCRIPTION_CACHE_FILE = DATA_FOLDER / "subscriptions.json"
CACHE_TIMEOUT = 24 * 60 * 60  # 24 Hours


def invalidate_cache():
    if os.path.exists(CLUSTER_CACHE_FILE):
        os.remove(CLUSTER_CACHE_FILE)
    if os.path.exists(SUBSCRIPTION_CACHE_FILE):
        os.remove(SUBSCRIPTION_CACHE_FILE)

def load_cache(what: CacheType):
    """Loads cached data if available and valid."""
    cache_file = CLUSTER_CACHE_FILE if what == CacheType.CLUSTER else SUBSCRIPTION_CACHE_FILE
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)
                if time.time() - cache_data["timestamp"] < CACHE_TIMEOUT:
                    return cache_data[what]
        except (json.JSONDecodeError, KeyError):
            pass  # Ignore and rebuild cache
    return None

def save_cache(what: CacheType, data: list):
    """Saves data to cache."""
    cache_file = CLUSTER_CACHE_FILE if what == CacheType.CLUSTER else SUBSCRIPTION_CACHE_FILE
    with open(cache_file, "w") as f:
        json.dump({"timestamp": time.time(), what: data}, f)