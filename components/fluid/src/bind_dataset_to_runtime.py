from kfp import dsl
import utils
import common

# Bind a cache runtime to the given Dataset, default is AlluxioRuntime
@dsl.component(
    base_image=common.base_image,
    target_image=common.target_image
)
def bind_dataset_to_runtime(
    dataset_name: str,
    namespace: str,
    cache_capacity: float,
    runtime_type: str = "alluxio",
    cache_medium: str = "MEM",
    cache_replicas: int = 1
):
    import logging
    runtime_type = utils.convert_runtime_type(runtime_type)
    if runtime_type == None:
        logging.error(f"Failed to bind Dataset \"{namespace}/{dataset_name}\" because argument runtime_type must be one of [\"alluxio\", \"jindo\", \"juicefs\", \"efc\", \"vineyard\"]")
        return
    if not utils.is_valid_cache_medium(cache_medium):
        logging.error(f"Failed to bind Dataset \"{namespace}/{dataset_name}\" because argument cache_medium must be one of [\"MEM\", \"SSD\", \"HDD\"]")
        return
    
    from fluid import FluidClient, ClientConfig

    fluid_client = FluidClient(ClientConfig())

    dataset = fluid_client.get_dataset(dataset_name=dataset_name, namespace=namespace)
    dataset.bind_runtime(
        runtime_type=runtime_type,
        replicas=cache_replicas,
        cache_capacity_GiB=cache_capacity,
        cache_medium=cache_medium,
        wait=True
    )

    logging.info(f"Bind Dataset \"{namespace}/{dataset_name}\" to runtime \"{namespace}/{dataset_name}\" successfully")