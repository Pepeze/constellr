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
    ):
        """Instantiate object holding data and methods for profiling of zarr downloads."""
        self.array_dimensions: tuple[int] = array_dimensions
        self.chunk_shapes: list[tuple[int]] = chunk_shapes
        self.local_directory: str = local_directory
        self.bucket: str = bucket
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
