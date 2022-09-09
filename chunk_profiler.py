from typing import Any

import numpy as np
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
