from kfp import dsl, compiler

# Create a Fluid dataset which contains data in S3 and bind it to an AlluxioRuntime
@dsl.component(packages_to_install=['git+https://github.com/fluid-cloudnative/fluid-client-python.git'])
def create_s3_dataset_with_alluxioruntime(
    dataset_name: str,
    namespace: str,
    mount_point: str,
    s3_endpoint: str,
    s3_region: str,
    cred_secret_name: str,
    cache_replicas: int,
    cache_capacity: float
):
    import logging
    import fluid
    from fluid import constants

    fluid_client = fluid.FluidClient(fluid.ClientConfig())

    options = {
        "alluxio.underfs.s4.endpoint": s3_endpoint,
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
        options=options
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

if __name__ == '__main__':
    compiler.Compiler().compile(create_s3_dataset_with_alluxioruntime, "./component.yaml")