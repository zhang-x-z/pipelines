from kfp import dsl, compiler

# Deploy a simple AlluxioRuntime
@dsl.component(packages_to_install=['git+https://github.com/fluid-cloudnative/fluid-client-python.git'])
def bind_dataset_to_runtime(
    dataset_name: str,
    namespace: str,
    runtime_type: str,
    cache_replicas: int,
    cache_capacity: float,
    cache_medium: str
):
    import logging
    from fluid import constants
    
    # TODO: validate cache_medium
    legal_runtime_type = {
        "alluxio": constants.ALLUXIO_RUNTIME_KIND,
        "jindo": constants.JINDO_RUNTIME_KIND,
        "juicefs": constants.JUICEFS_RUNTIME_KIND,
        "efc": constants.EFC_RUNTIME_KIND,
        "vineyard": constants.VINEYARD_RUNTIME_KIND
    }
    if runtime_type not in legal_runtime_type.keys():
        logging.info(f"Failed to bind Dataset \"{namespace}/{dataset_name}\" because argument runtime_type must be one of [\"alluxio\", \"jindo\", \"juicefs\", \"efc\", \"vineyard\"]")
        return
    
    import fluid

    fluid_client = fluid.FluidClient(fluid.ClientConfig())

    dataset = fluid_client.get_dataset(dataset_name=dataset_name, namespace=namespace)
    dataset.bind_runtime(
        runtime_type=legal_runtime_type[runtime_type],
        replicas=cache_replicas,
        cache_capacity_GiB=cache_capacity,
        cache_medium=cache_medium,
        wait=True
    )

    logging.info(f"Bind Dataset \"{namespace}/{dataset_name}\" to runtime \"{namespace}/{dataset_name}\" successfully")

if __name__ == '__main__':
    compiler.Compiler().compile(bind_dataset_to_runtime, "./component.yaml")