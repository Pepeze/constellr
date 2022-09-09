from chunk_profiler import ChunkProfiler

ARRAY_DIMENSIONS: tuple[int] = (1000, 100, 150)
CHUNK_SHAPES: list[tuple[int]] = [(1, None, None), (10, None, None), (100, None, None), (1000, None, None)]


if __name__ == "__main__":
    chunk_profiler: ChunkProfiler = ChunkProfiler(array_dimensions=ARRAY_DIMENSIONS, chunk_shapes=CHUNK_SHAPES)

    print("Data generation started")
    chunk_profiler.generate_data()
    print("Data generation completed")
