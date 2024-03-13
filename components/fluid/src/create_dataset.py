from kfp import dsl
import common

# Preload the Dataset with given name and namespace
@dsl.component(
    base_image=common.base_image,
    target_image=common.target_image
)
def create_dataset(
    dataset_name: str,
    namespace: str,
    mount_point: str,
    options: dict = None,
    cred_secret_name: str = None,
    cred_secret_options: dict = None,
    mount_path: str = None,
    mount_name: str = None,
    mode: str = "ReadOnly",
):
    """Component to create a Dataset.

    Arguments:
        dataset_name (str): Name of the Dataset.
        namespace (str): Namespace of the Dataset.
        mount_point (str): Mount point of the source.
            E.g. use `s3://your-bucket` to mount a S3 bucket.
        options (dict): Options which can be used in cache runtime. Defaults to None.
            E.g. you can set Alluxio configurations in this field if you will bind this Dataset to AlluxioRuntime:
            ```python
            options = {
                "alluxio.underfs.s3.endpoint": "https://your-s3-endpoint",
                "alluxio.underfs.s3.endpoint.region": "your-s3-region"
            }
            ``` 
        cred_secret_name (str, optional): Name of the secret which is used to access external storage (e.g. S3). Defaults to None.
        cred_secret_options (dict, optional): Contents in secret `<cred_secret_name>`. Defaults to None.
            E.g. If you create a secret to access S3 with AlluxioRuntime like:
            ```yaml
            apiVersion: v1
            kind: Secret
            metadata:
              name: s3-secret
            stringData:
              s3-accessKeyId: <your-access-key-id>
              s3-secretKey: <your-secret-key>
            ```
            You should set `cred_secret_name` and `cred_secret_options` to:
            ```python
            cred_secret_name = "s3-secret"
            cred_secret_options = {
                "s3a.accessKeyId": "s3-accessKeyId",
                "s3a.secretKey": "s3-secretKey"
            }
            ```
            Note that you should set `cred_secret_name` and `cred_secret_options` together.
        mount_path (str, optional): Path to mount in cache runtime. When this field is None, the mount path will be set to `/<mount_name>`. Defaults to None.
        mount_name (str, optional): Name of this mount. When this field is None, it will be set to `dataset_name`. Defaults to None.
        mode (str, optional): Mode of this Dataset. Must be one of ["ReadOnly", "ReadWrite"]. Defaults to "ReadOnly".
    """
    import logging
    from fluid import FluidClient, ClientConfig
    
    fluid_client = FluidClient(ClientConfig())

    if mount_name == None or len(mount_name) == 0:
        mount_name = dataset_name
    
    fluid_client.create_dataset(
        dataset_name=dataset_name,
        namespace=namespace,
        mount_name=mount_name,
        mount_point=mount_point,
        mount_path=mount_path,
        options=options,
        mode=mode,
        cred_secret_name=cred_secret_name,
        cred_secret_options=cred_secret_options
    )
    
    logging.info(f"Create Dataset \"{namespace}/{dataset_name}\" successfully")
