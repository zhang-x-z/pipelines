base_image = "python:3.8"


fluid_pysdk_name = "fluid-pysdk"
fluid_pysdk_version = "1.0.0a1"
fluid_pysdk = f"{fluid_pysdk_name}=={fluid_pysdk_version}"

image_repo = "fluidcloudnative"
image_name = "fluid-pipline-components"
image_tag = "v0.0.1"
target_image = f"{image_repo}/{image_name}:{image_tag}"