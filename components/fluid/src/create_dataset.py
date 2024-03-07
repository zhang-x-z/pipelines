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
    options: dict,
    cred_secret_name: str = None,
    cred_secret_options: dict = None,
    mount_path: str = None,
    mount_name: str = None,
    mode: str = "ReadOnly",
):
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
