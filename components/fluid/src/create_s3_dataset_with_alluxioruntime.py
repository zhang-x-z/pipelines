from kfp import dsl
import common

# Create a Fluid dataset which contains data in S3 and bind it to an AlluxioRuntime
@dsl.component(
    base_image=common.base_image,
    packages_to_install=[common.fluid_pysdk],
    target_image=common.target_image
)
def create_s3_dataset_with_alluxioruntime(
    dataset_name: str,
    namespace: str,
    mount_point: str,
    s3_endpoint: str,
    s3_region: str,
    cache_capacity: float,
    replicas: int = 1,
    cred_secret_name: str = "s3-secret",
    dataset_mode: str = "ReadOnly"
):
    """Component to create a Dataset which uses S3 as external storage and bind it to an AlluxioRuntime.

    Args:
        dataset_name (str): Name of the Dataset.
        namespace (str): Namespace of the Dataset.
        mount_point (str): Mount point of the source.
        s3_endpoint (str): Endpoint of the S3 bucket you want to mount.
        s3_region (str): Region of the S3 bucket you want to mount.
        cache_capacity (float): Cache capacity (GiB) of one cache runtime worker.
        replicas (int, optional): Number of cache runtime workers. Defaults to 1.
        cred_secret_name (str, optional): Name of the secret which is used to access S3. Defaults to "s3-secret".
        dataset_mode (str, optional): Mode of this Dataset. Must be one of ["ReadOnly", "ReadWrite"]. Defaults to "ReadOnly".
    
    When using this component, the secret which used to access S3 should have contents like this:
    ```yaml
    apiVersion: v1
    kind: Secret
    metadata:
        name: <secret-name, same as filed cred_secret_name>
    stringData:
        aws.accessKeyId: <your-access-key-id>
        aws.secretKey: <your-secret-key>
    ```
    
    """
    import logging
    from fluid import FluidClient, ClientConfig, constants

    fluid_client = FluidClient(ClientConfig())

    options = {
        "alluxio.underfs.s3.endpoint": s3_endpoint,
        "alluxio.underfs.s3.endpoint.region": s3_region,
        "alluxio.underfs.s3.disable.dns.buckets": "true",
        "alluxio.underfs.s3.disable.inherit.acl": "false"
    }

    cred_secret_options = {
        "aws.accessKeyId": "aws.accessKeyId",
        "aws.secretKey": "aws.secretKey",
    }

    fluid_client.create_dataset(
        dataset_name=dataset_name,
        namespace=namespace,
        mount_name=dataset_name,
        mount_point=mount_point,
        cred_secret_name=cred_secret_name,
        cred_secret_options=cred_secret_options,
        options=options,
        mode=dataset_mode
    )
    
    dataset = fluid_client.get_dataset(dataset_name=dataset_name, namespace=namespace)
    
    dataset.bind_runtime(
        runtime_type=constants.ALLUXIO_RUNTIME_KIND,
        replicas=replicas,
        cache_capacity_GiB=cache_capacity,
        wait=True
    )
    
    logging.info(f"Dataset \"{namespace}/{dataset_name}\" is created and bond to AlluxioRuntime \"{namespace}/{dataset_name}\" successfully")
    logging.info(f"Cache replicas: {replicas}, Cache capacity: {cache_capacity}, Total cache capacity: {replicas * cache_capacity}")
