from kfp import dsl
import common

# Migrate the Dataset with given name and namespace
@dsl.component(
    base_image=common.base_image,
    target_image=common.target_image
)
def migrate_dataset(
    dataset_name: str,
    namespace: str,
    migrate_path: str,
    migrate_direction: str,
    external_storage: str
):
    import logging
    from fluid import FluidClient, ClientConfig
    
    fluid_client = FluidClient(ClientConfig())
    fluid_client.get_dataset(dataset_name=dataset_name, namespace=namespace).migrate(path=migrate_path, migrate_direction=migrate_direction, external_storage=external_storage)
    
    logging.info(f"Migrate Dataset \"{namespace}/{dataset_name}\" successfully")
