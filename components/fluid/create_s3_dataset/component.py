from kfp import dsl, compiler

# Create a Fluid dataset which contains data in S3.
@dsl.component(packages_to_install=['git+https://github.com/fluid-cloudnative/fluid-client-python.git'])
def create_s3_dataset(dataset_name: str, namespace: str, mount_point: str, s3_endpoint: str, s3_region: str):
    import logging
    import fluid
    from kubernetes import client
    fluid_client = fluid.FluidClient()

    FLUID_GROUP = "data.fluid.io"
    FLUID_VERSION = "v1alpha1"

    # This is an sample which use some pre-defined options.
    # Users can change these code customily
    dataset = fluid.Dataset(
        api_version="%s/%s" % (FLUID_GROUP, FLUID_VERSION),
        kind="Dataset",
        metadata=client.V1ObjectMeta(
            name=dataset_name,
            namespace=namespace
        ),
        spec=fluid.DatasetSpec(
            mounts=[
                fluid.Mount(
                    mount_point=mount_point,
                    name=dataset_name,
                    options={
                        "alluxio.underfs.s3.endpoint": s3_endpoint,
                        "alluxio.underfs.s3.endpoint.region": s3_region,
                        "alluxio.underfs.s3.disable.dns.buckets": "true",
                        "alluxio.underfs.s3.disable.inherit.acl": "false"
                    },
                    encrypt_options=[
                        {
                            "name": "aws.accessKeyId",
                            "valueFrom": {
                              "secretKeyRef": {
                                "name": "s3-secret",
                                "key": "aws.accessKeyId"
                              }
                            }
                        },
                        {
                            "name": "aws.secretKey",
                            "valueFrom": {
                              "secretKeyRef": {
                                "name": "s3-secret",
                                "key": "aws.secretKey"
                              }
                            }
                        }
                    ]
                )
            ]
        )
    )

    fluid_client.create_dataset(dataset)
    
    logging.info(f"Dataset \"{dataset.metadata.namespace}/{dataset.metadata.name}\" created successfully")

if __name__ == '__main__':
    compiler.Compiler().compile(create_s3_dataset, "./component.yaml")