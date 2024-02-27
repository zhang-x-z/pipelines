from kfp import dsl, compiler

# Delete the dataset
@dsl.component(packages_to_install=['git+https://github.com/fluid-cloudnative/fluid-client-python.git'])
def delete_dataset(dataset_name: str, namespace: str):
    import logging
    from fluid import FluidClient
    
    fluid_client = FluidClient()
    fluid_client.delete_dataset(name=dataset_name, namespace=namespace, wait_until_cleaned_up=True)

    logging.info(f"Cleanup Dataset \"{namespace}/{dataset_name}\" successfully!")

if __name__ == '__main__':
    compiler.Compiler().compile(delete_dataset, "./component.yaml")