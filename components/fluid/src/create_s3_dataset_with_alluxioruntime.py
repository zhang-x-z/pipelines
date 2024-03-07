from kfp import dsl
import common

# Create a Fluid dataset which contains data in S3 and bind it to an AlluxioRuntime
@dsl.component(
    base_image=common.base_image,
    target_image=common.target_image
)
def create_s3_dataset_with_alluxioruntime(
    dataset_name: str,
    namespace: str,
    mount_point: str,
    s3_endpoint: str,
    s3_region: str,
    cache_capacity: float,
    cache_replicas: int = 1,
    cred_secret_name: str = "s3-secret",
    dataset_mode: str = "ReadOnly"
):
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
        replicas=cache_replicas,
        cache_capacity_GiB=cache_capacity,
        wait=True
    )
    
    logging.info(f"Dataset \"{namespace}/{dataset_name}\" is created and bond to AlluxioRuntime \"{namespace}/{dataset_name}\" successfully")
    logging.info(f"Cache replicas: {cache_replicas}, Cache capacity: {cache_capacity}, Total cache capacity: {cache_replicas * cache_capacity}")
