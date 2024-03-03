from kfp import dsl, compiler

# Preheat the dataset with specific dataset name and namespace
@dsl.component(packages_to_install=['git+https://github.com/fluid-cloudnative/fluid-client-python.git'])
def preload_dataset(
    dataset_name: str,
    namespace: str,
    target_path: str = "/",
    load_metadata: bool = False
):
    import logging
    import fluid
    
    fluid_client = fluid.FluidClient(fluid.ClientConfig())
    fluid_client.get_dataset(dataset_name=dataset_name, namespace=namespace).preload(target_path=target_path, load_metadata=load_metadata).run()
    
    logging.info(f"Load Dataset \"{namespace}/{dataset_name}\"  successfully")

if __name__ == '__main__':
    compiler.Compiler().compile(preload_dataset, "./component.yaml")