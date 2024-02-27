from kfp import dsl, compiler

# Deploy a simple AlluxioRuntime
@dsl.component(packages_to_install=['git+https://github.com/fluid-cloudnative/fluid-client-python.git'])
def create_alluxioruntime(dataset_name: str, namespace: str):
    import logging
    from fluid import AlluxioRuntime, AlluxioRuntimeSpec, models, FluidClient
    from kubernetes import client as k8s_client

    fluid_client = FluidClient()

    FLUID_GROUP = "data.fluid.io"
    FLUID_VERSION = "v1alpha1"

    replicas = 1

    # This is the simplest configuration for AlluxioRuntime, you can change the AlluxioRuntime according to your needs
    alluxio_runtime = AlluxioRuntime(
        api_version="%s/%s" % (FLUID_GROUP, FLUID_VERSION),
        kind="AlluxioRuntime",
        metadata=k8s_client.V1ObjectMeta(
            name=dataset_name,
            namespace=namespace
        ),
        spec=AlluxioRuntimeSpec(
            replicas=replicas,
            tieredstore=models.TieredStore([models.Level('0.95', '0.7', 'MEM', '/dev/shm', '2Gi', volume_type=None)])
        )
    )

    fluid_client.create_runtime(alluxio_runtime)


    logging.info(f"Runtime \"{alluxio_runtime.metadata.namespace}/{alluxio_runtime.metadata.name}\" created successfully")

if __name__ == '__main__':
    compiler.Compiler().compile(create_alluxioruntime, "./component.yaml")