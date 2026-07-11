"""
Tile cache inspection and management utilities.

The tile cache lives at ~/.tiffy/tile_cache/{source_id}/{zoom}/{tx}/{ty}.png
and persists across runs (see core/exporter.py) so retries and overlapping
polygons can reuse previously downloaded tiles instead of re-fetching them.
"""

import os
import shutil
from typing import Dict, Optional, Tuple

from .tile_sources import get_source_by_id


def default_cache_dir() -> str:
    """Default tile cache directory: ~/.tiffy/tile_cache"""
    return os.path.join(os.path.expanduser('~'), '.tiffy', 'tile_cache')


def get_cache_stats(cache_dir: str) -> Dict:
    """
    Compute cache size and tile count, broken down by tile source.

    Args:
        cache_dir: Tile cache root directory

    Returns:
        Dict with keys: total_bytes, total_files, by_source
        (by_source maps source_id -> {'bytes': int, 'files': int, 'name': str})
    """
    stats = {'total_bytes': 0, 'total_files': 0, 'by_source': {}}

    if not os.path.isdir(cache_dir):
        return stats

    for source_id in sorted(os.listdir(cache_dir)):
        source_path = os.path.join(cache_dir, source_id)
        if not os.path.isdir(source_path):
            continue

        size = 0
        count = 0
        for root, _dirs, files in os.walk(source_path):
            for filename in files:
                try:
                    size += os.path.getsize(os.path.join(root, filename))
                    count += 1
                except OSError:
                    pass

        source = get_source_by_id(source_id)
        stats['by_source'][source_id] = {
            'bytes': size,
            'files': count,
            'name': source.name if source else source_id,
        }
        stats['total_bytes'] += size
        stats['total_files'] += count

    return stats


def clear_cache(cache_dir: str, source_id: Optional[str] = None) -> Tuple[bool, str]:
    """
    Delete cached tiles.

    Args:
        cache_dir: Tile cache root directory
        source_id: If given, only clear this source's subdirectory; otherwise clear everything

    Returns:
        Tuple of (success, message)
    """
    target = cache_dir if source_id is None else os.path.join(cache_dir, source_id)

    if not os.path.isdir(target):
        return True, "Nothing to clear"

    try:
        shutil.rmtree(target)
        return True, "Cache cleared"
    except Exception as e:
        return False, f"Failed to clear cache: {e}"
