from kfp import dsl
import common

# Delete the Dataset with given name and namespace
@dsl.component(
    base_image=common.base_image,
    target_image=common.target_image
)
def delete_dataset(dataset_name: str, namespace: str):
    import logging
    from fluid import FluidClient, ClientConfig
    
    fluid_client = FluidClient(ClientConfig())
    fluid_client.cleanup_dataset(name=dataset_name, namespace=namespace, wait=True)

    logging.info(f"Cleanup Dataset \"{namespace}/{dataset_name}\" successfully!")
