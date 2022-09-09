import os
import shutil
import time
from typing import Any

import numpy as np
import s3fs
import zarr


class ChunkProfiler:
    def __init__(
        self,
        array_dimensions: tuple[int],
        chunk_shapes: list[tuple[int]],
        local_directory: str = "downloads",
        bucket: str = "constellr",
        iterations: int = 10,
    ):
        """Instantiate object holding data and methods for profiling of zarr downloads."""
        self.array_dimensions: tuple[int] = array_dimensions
        self.chunk_shapes: list[tuple[int]] = chunk_shapes
        self.local_directory: str = local_directory
        self.bucket: str = bucket
        self.iterations: int = iterations
        self.results: dict[str, Any] = {}
        self.file_system: s3fs.S3FileSystem = s3fs.S3FileSystem(asynchronous=False)

    def generate_data(self):
        """Generate chunked zarr arrays and instantiate storage variables."""
        np_array: np.ndarray = np.random.rand(*self.array_dimensions)
        for chunk_shape in self.chunk_shapes:
            zarr_array: zarr.core.Array = zarr.array(np_array, chunks=chunk_shape)
            number_of_chunks: int = zarr_array.nchunks
            partition: str = f"chunks={number_of_chunks}"
            local_path: str = f"{self.local_directory}/{partition}"
            remote_path: str = f"s3//{self.bucket}/{partition}"

            self.results[number_of_chunks] = {
                "zarr_array": zarr_array,
                "chunk_shape": chunk_shape,
                "partition": partition,
                "local_path": local_path,
                "remote_path": remote_path,
            }
            print(f"Generated data with {zarr_array.nchunks} chunks")

    def upload_files(self):
        """Upload generated chunked zarr arrays to S3 bucket."""
        for chunk in self.results.values():
            start_time: float = time.time()

            zarr.save(s3fs.S3Map(chunk["remote_path"], s3=self.file_system), chunk["zarr_array"])

            end_time: float = time.time()
            elapsed_time: float = end_time - start_time
            chunk["upload_time"] = elapsed_time
            print(f"Upload of {chunk['partition']} took {round(elapsed_time, 1)} seconds")

    def download_files(self):
        """Download files for each chunk size from S3 bucket. Downloading is repeated for more reliable results."""
        for chunk in self.results.values():
            chunk["download_times"]: list[int] = []
            for iteration in range(self.iterations):
                self._clean_local_directory()
                start_time: float = time.time()

                zarr_array: zarr.core.Array = zarr.open(s3fs.S3Map(chunk["remote_path"], s3=self.file_system))
                zarr.save(chunk["local_path"], zarr_array)

                end_time: float = time.time()
                elapsed_time: float = end_time - start_time
                chunk["download_times"].append(elapsed_time)
                print(
                    f"Iteration {iteration}: Download from {chunk['remote_path']} took {round(elapsed_time, 1)} seconds"
                )
            chunk["chunk_size_mb"]: float = os.path.getsize(f"{chunk['local_path']}/0.0.0") / 1024**2

    def _clean_local_directory(self):
        """Remove the local directory if it exists."""
        shutil.rmtree(self.local_directory, ignore_errors=True)
