from chunk_profiler import ChunkProfiler

ARRAY_DIMENSIONS: tuple[int] = (1000, 100, 150)
CHUNK_SHAPES: list[tuple[int]] = [(1, None, None), (10, None, None), (100, None, None), (1000, None, None)]

# Choose between "s3", "gcs" and "abfs".
STORAGE_SERVICE: str = "s3"


if __name__ == "__main__":
    chunk_profiler: ChunkProfiler = ChunkProfiler(
        array_dimensions=ARRAY_DIMENSIONS, chunk_shapes=CHUNK_SHAPES, storage_service=STORAGE_SERVICE
    )

    print("Data generation started")
    chunk_profiler.generate_data()
    print("Data generation completed")

    print("Data upload started")
    chunk_profiler.upload_files()
    print("Data upload completed")

    print("Data download started")
    chunk_profiler.download_files()
    print("Data download completed")

    print("Average calculation started")
    chunk_profiler.calculate_averages()
    print("Average calculation completed")

    print("Result saving started")
    chunk_profiler.save_results()
    print("Result saving completed")
