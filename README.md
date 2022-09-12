# Chunk Profiler

## Introduction

This repository is a tool for profiling of `zarr` file downloads from cloud object storage.
Many well-known storage solutions are supported, such as `AWS S3`, `Google Cloud Storage (GCS)`
and `Azure Blog Storage (ABFS)`. Using the `ChunkProfiler` class, `zarr` arrays are generated from `numpy` arrays.
The array shape is set by the user. For example, a `numpy` array of 8-byte random integers and shape (1000, 100, 150)
results in a `zarr` array that requires approximately 100 MB of disk space when using standard compression.
After array generation a desired chunking is applied. The `zarr` chunks are then uploaded to a selected object storage.
Finally, the chunked files are downloaded multiple times, and the elapsed times are averaged. The results are saved
in a `JSON` file where the keys are the number of chunks.
`Zarr` uses asynchronous I/O operations under the hood by default through the `fsspec` package.

## Setup

- Create a virtual environment: `virtualenv venv -p 3.9`.
- Activate the virtual environment: `source venv/bin/activate`.
- Install `Python` requirements: `pip install -r requirements.txt`.
- Set the desired cloud service in the `main.py` file: `STORAGE_SERVICE: str = "<s3|gcs|abfs>"`.
- Set up the corresponding cloud service environment (see `S3`, `GCS` and `ABFS` headings below).
- Run main file: `python3 main.py`.

### S3

- Create and setup an `AWS` account.
- Create a user having programmatic access and all `S3` rights.
- Take note of the credentials.
- Create an `S3` bucket.
- Set credentials as environment variables: \
`export AWS_ACCESS_KEY_ID="<access_key_id_from_iam_user_credentials>"` \
`export AWS_SECRET_ACCESS_KEY="<secret_access_key_from_iam_user_credentials>"`

### GCP

- Create and setup a `GCP` account.
- Create `Service Account` dedicated to `Cloud Storage`, setting the `Role` to `Owner`.
- Go to the created service account, create a `JSON` key, and save it.
- Create a `Cloud Storage` bucket.
- Set credentials as environment variables: \
`export GOOGLE_APPLICATION_CREDENTIALS="<path_to_json_credentials_file>"`

### ABFS

- Create and setup an `Azure` account.
- Create a `Storage Account`.
- If needed, allow local IP by adding firewall exception.
- Create `Azure Blob` container.
- Set credentials as environment variables: \
`export AZURE_STORAGE_ACCOUNT="<name_of_azure_storage_account>"` \
`export AZURE_STORAGE_CONNECTION_STRING="<connection_string_for_storage_account>"`

### S3 VPC

- Create `EC2` instance on pre-existing public `VPC` with a pre-existing subnet mask.
- Download `EC2` `pem` key to local `.ssh` directory.
- Change permissions of `pem` file to `600` and add it to the `ssh-agent`.
- Use the default `AWS` security group but add an incoming rule to allow all `SSH` traffic.
- Create `VPC` endpoint for the `S3` service using the pre-existing `VPC` and pre-existing route table.
- Start `EC2` instance and install `git`.
- Clone this repository onto the instance.

## Results

The table below shows the results from a run using a `zarr` array shape of (1000, 100, 150) with the first dimension
chunked by 1, 10, 100 and 1000. Despite an output that depends heavily on internet stability, a conclusion one can
draw is that a smaller number of large files seem to be downloaded faster than a larger number of small files. It also
seems like there are diminishing returns starting somewhere after a file size of 10 MB (10 chunks). This means that
the download speed does not increase significantly when file sizes increase beyond that point.

In general, it seems like the 3 large cloud providers have similar download speeds, with `S3` possibly being
slightly slower. One very clear result, however, is the improvement in download speed when cloud computing is used in
favor of local computing. This alternative was only tried on `AWS` using an `EC2` machine and a `VPC` endpoint.
A `t2.small` machine with 1 virtual CPU and 2 GB of RAM was used. The results show a factor of 5-30 in speed improvement
when comparing files transferred over internet and files transferred over `VPC`. This is due to the low latency within
`AWS`, and similar improvements would be expected when setting this up in any of the other cloud service providers.

<table>
<tr>
	<td>Number of Chunks</td><td>Chunk Shape</td><td>File Size (MB)</td>
	<td>S3 Download Time (s)</td><td>GCS Download Time (s)</td>
	<td>ABFS Download Time (s)</td><td>S3 VPC Download Time (s)</td>
</tr>
<tr><td>1</td><td>(1000, 100, 150)</td><td>100</td><td>43.3</td><td>30.0</td><td>25.3</td><td>1.4</td></tr>
<tr><td>10</td><td>(100, 100, 150)</td><td>10</td><td>47.7</td><td>31.6</td><td>27.6</td><td>1.4</td></tr>
<tr><td>100</td><td>(10, 100, 150)</td><td>1</td><td>43.8</td><td>36.9</td><td>45.3</td><td>3.6</td></tr>
<tr><td>1000</td><td>(1, 100, 150)</td><td>0.1</td><td>109.2</td><td>114.8</td><td>101.8</td><td>22.2</td></tr>
</table>

### Raw Output Example

When running the `main.py` file, the upload speed and average download speed for each chunk shape is saved
to a `JSON` file. An example of this output for the `S3` storage service over `VPC` is shown below.

```json
{
  "1000": {
		"chunk_shape": [
			1,
			null,
			null
		],
		"partition": "chunks=1000",
		"local_path": "downloads/chunks=1000",
		"remote_path": "s3://constellr/chunks=1000",
		"upload_time": 7.276594638824463,
		"download_times": [
			26.925528287887573,
			20.321176052093506,
			20.75893783569336,
			20.369073629379272,
			20.212913036346436,
			23.45077657699585,
			22.960577726364136,
			21.809746980667114,
			23.206907033920288,
			22.10556197166443
		],
		"chunk_size_mb": 0.1002511978149414,
		"average_download_time": 22.2
	},
	"100": {
		"chunk_shape": [
			10,
			null,
			null
		],
		"partition": "chunks=100",
		"local_path": "downloads/chunks=100",
		"remote_path": "s3://constellr/chunks=100",
		"upload_time": 1.8218750953674316,
		"download_times": [
			6.921512842178345,
			4.430762767791748,
			3.346081495285034,
			3.0426602363586426,
			2.9514966011047363,
			3.200324773788452,
			3.1676952838897705,
			2.9761056900024414,
			2.9376626014709473,
			3.006852626800537
		],
		"chunk_size_mb": 1.0025835037231445,
		"average_download_time": 3.6
	},
	"10": {
		"chunk_shape": [
			100,
			null,
			null
		],
		"partition": "chunks=10",
		"local_path": "downloads/chunks=10",
		"remote_path": "s3://constellr/chunks=10",
		"upload_time": 1.1325838565826416,
		"download_times": [
			1.9918303489685059,
			1.5557591915130615,
			1.3683297634124756,
			1.3635873794555664,
			1.3600881099700928,
			1.340242624282837,
			1.3756041526794434,
			1.3311495780944824,
			1.3284549713134766,
			1.342226266860962
		],
		"chunk_size_mb": 10.021635055541992,
		"average_download_time": 1.4
	},
	"1": {
		"chunk_shape": [
			1000,
			null,
			null
		],
		"partition": "chunks=1",
		"local_path": "downloads/chunks=1",
		"remote_path": "s3://constellr/chunks=1",
		"upload_time": 1.7651524543762207,
		"download_times": [
			1.513777494430542,
			1.48093843460083,
			1.466902256011963,
			1.5079240798950195,
			1.4052093029022217,
			1.4126954078674316,
			1.406984806060791,
			1.4051237106323242,
			1.4036109447479248,
			1.4049556255340576
		],
		"chunk_size_mb": 100.2011489868164,
		"average_download_time": 1.4
	}
}
```