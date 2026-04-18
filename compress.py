#!/usr/bin/env python3
"""
Recompress a GeoTIFF for maximum file size reduction.

Uses lossless DEFLATE compression at level 9 with a horizontal predictor,
which typically reduces satellite GeoTIFFs by 40-70%. Decompression is
slower than LZW but the pixel data is identical.

Reads in 256-row chunks — safe for files of any size.

Usage:
    python compress.py input.tif output.tif
    python compress.py input.tif output.tif --method zstd
"""

import argparse
import os
import sys
import time
import numpy as np
import rasterio
from rasterio import windows


def compress(input_path: str, output_path: str, method: str = 'deflate'):
    if not os.path.exists(input_path):
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    in_size_gb = os.path.getsize(input_path) / 1e9

    if method == 'zstd':
        compress_opts = {'compress': 'ZSTD', 'ZSTD_LEVEL': 22}
        method_label = 'ZSTD level 22'
    else:
        compress_opts = {'compress': 'DEFLATE', 'ZLEVEL': 9}
        method_label = 'DEFLATE level 9'

    print(f"Input:   {input_path}  ({in_size_gb:.1f} GB)")
    print(f"Output:  {output_path}")
    print(f"Method:  {method_label} + horizontal predictor + tiled")
    print()

    with rasterio.open(input_path) as src:
        out_meta = src.meta.copy()
        out_meta.update({
            **compress_opts,
            'tiled': True,
            'blockxsize': 512,
            'blockysize': 512,
            'PREDICTOR': 2,   # Horizontal differencing — big win for imagery
            'BIGTIFF': 'YES',
        })

        height = src.height
        width = src.width
        CHUNK_ROWS = 256
        total_chunks = (height + CHUNK_ROWS - 1) // CHUNK_ROWS
        start = time.time()

        with rasterio.open(output_path, 'w', **out_meta) as dst:
            for chunk_idx, row_off in enumerate(range(0, height, CHUNK_ROWS)):
                chunk_h = min(CHUNK_ROWS, height - row_off)
                win = windows.Window(0, row_off, width, chunk_h)

                data = src.read(window=win)
                dst.write(data, window=win)

                done = row_off + chunk_h
                pct = done / height * 100
                elapsed = time.time() - start
                eta = (elapsed / done) * (height - done) if done < height else 0
                print(f"\r  {pct:.1f}%  |  {elapsed/60:.1f}m elapsed  |  ETA {eta/60:.1f}m   ",
                      end='', flush=True)

    print()
    out_size_gb = os.path.getsize(output_path) / 1e9
    ratio = out_size_gb / in_size_gb * 100
    elapsed = time.time() - start
    print(f"\nDone in {elapsed/60:.1f} minutes")
    print(f"Input:  {in_size_gb:.2f} GB")
    print(f"Output: {out_size_gb:.2f} GB  ({ratio:.0f}% of original, {100-ratio:.0f}% smaller)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Recompress a GeoTIFF for maximum lossless compression.'
    )
    parser.add_argument('input',  help='Input GeoTIFF path')
    parser.add_argument('output', help='Output GeoTIFF path')
    parser.add_argument(
        '--method',
        choices=['deflate', 'zstd'],
        default='deflate',
        help='Compression algorithm (default: deflate). zstd compresses better but needs GDAL 2.3+.'
    )
    args = parser.parse_args()
    compress(args.input, args.output, args.method)
