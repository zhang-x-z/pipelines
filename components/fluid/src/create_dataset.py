from kfp import dsl
import common

# Preload the Dataset with given name and namespace
@dsl.component(
    base_image=common.base_image,
    packages_to_install=[common.fluid_pysdk],
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
    """Component to create a Dataset.

    Args:
        dataset_name (str): Name of the Dataset.
        namespace (str): Namespace of the Dataset.
        mount_point (str): Mount point of the source.
        options (dict): Options which may be used in cache runtime.
        cred_secret_name (str, optional): Name of the secret which is used to access external storage (e.g. S3). Defaults to None.
        cred_secret_options (dict, optional): Contents in secret `<cred_secret_name>`. Defaults to None.
        mount_path (str, optional): Path to mount in cache runtime. When this field is None, the mount path will be `/<mount_name>`. Defaults to None.
        mount_name (str, optional): Name of this mount. When this field is None, it will be set to `<dataset_name>`. Defaults to None.
        mode (str, optional): Mode of this Dataset. Must be one of ["ReadOnly", "ReadWrite"]. Defaults to "ReadOnly".
    """
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
