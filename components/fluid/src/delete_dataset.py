from kfp import dsl, compiler
import common

# Delete the Dataset with given name and namespace
@dsl.component(
    base_image=common.base_image,
    target_image=common.target_image
)
def delete_dataset(dataset_name: str, namespace: str):
    """Component to delete a Dataset.

    Args:
        dataset_name (str): Name of the Dataset.
        namespace (str): Namespace of the Dataset.
    """
    import logging
    from fluid import FluidClient, ClientConfig
    
    fluid_client = FluidClient(ClientConfig())
    fluid_client.cleanup_dataset(name=dataset_name, namespace=namespace, wait=True)

    logging.info(f"Cleanup Dataset \"{namespace}/{dataset_name}\" successfully!")

if __name__ == "__main__":
    compiler.Compiler().compile(delete_dataset, package_path="./test.yaml")