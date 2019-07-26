import s3fs
import dask.array as da
import zarr


def write(dask_array: da, url: str, profile_name: str="spacetx"):
    if url.startswith("s3://"):

        url = url.replace(" ", '-')
        url = url.rstrip("/")
        url = url.replace("s3://", "")

        if url.count("/") > 1:
            raise ValueError("I haven't figured out how to write groups yet, this will fail.")

        s3 = s3fs.S3FileSystem(profile_name=profile_name)
        root = f"{url}.regions.zarr"
        store = s3fs.S3Map(root=root, s3=s3, check=False)
        z = zarr.create(shape=dask_array.shape, dtype=dask_array.dtype, store=store)
        dask_array.to_zarr(z)
