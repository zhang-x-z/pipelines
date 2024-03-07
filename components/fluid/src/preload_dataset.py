from kfp import dsl
import common

# Preload the Dataset with given name and namespace
@dsl.component(
    base_image=common.base_image,
    packages_to_install=[common.fluid_pysdk],
    target_image=common.target_image
)
def preload_dataset(
    dataset_name: str,
    namespace: str,
    target_path: str = "/",
    load_metadata: bool = False
):
    """Component to preload the Dataset.

    Args:
        dataset_name (str): Name of the Dataset.
        namespace (str): Namespace of the Dataset.
        target_path (str, optional): Path which needs to preload data. Defaults to "/".
        load_metadata (bool, optional): Whether to load metadata. Defaults to False.
    """
    import logging
    from fluid import FluidClient, ClientConfig
    
    fluid_client = FluidClient(ClientConfig())
    fluid_client.get_dataset(dataset_name=dataset_name, namespace=namespace).preload(target_path=target_path, load_metadata=load_metadata).run()
    
    logging.info(f"Load Dataset \"{namespace}/{dataset_name}\" successfully")
