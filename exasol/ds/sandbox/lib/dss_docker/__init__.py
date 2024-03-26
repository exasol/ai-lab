from .create_image import DssDockerImage, DEFAULT_ORG_AND_REPOSITORY
from .push_image import DockerRegistry

# Names of environment variables for user and password to access docker
# services.  This is especially required for rate limits docker hub sometimes
# applies for tests running on AWS CodeBuild.

USER_ENV = "DOCKER_REGISTRY_USER"
PASSWORD_ENV = "DOCKER_REGISTRY_PASSWORD"
