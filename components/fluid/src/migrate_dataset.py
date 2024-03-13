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
    external_storage_uri: str,
    external_storage_encrypt_options: dict = None
):
    """Component to migrate a Dataset.

    Args:
        dataset_name (str): Name of the Dataset.
        namespace (str): Namespace of the Dataset.
        migrate_path (str): Path to be migrated.
        migrate_direction (str): The direction of migration. Must be either "from" or "to".
            "from" means migrate from external storage to the Dataset. "to" means migrate from the Dataset to external storage.
        external_storage_uri (str): External storage uri used for migration.
        external_storage_encrypt_options (dict): Encrypt options used to access the external storage. Defaults to None.
    """
    import logging
    from fluid import FluidClient, ClientConfig
    from fluid.models.external_storage import ExternalStorage
    
    fluid_client = FluidClient(ClientConfig())
    external_storage = ExternalStorage(uri=external_storage_uri, encrypt_options=external_storage_encrypt_options)
    fluid_client.get_dataset(dataset_name=dataset_name, namespace=namespace).migrate(path=migrate_path, migrate_direction=migrate_direction, external_storage=external_storage)
    
    logging.info(f"Migrate Dataset \"{namespace}/{dataset_name}\" successfully")
