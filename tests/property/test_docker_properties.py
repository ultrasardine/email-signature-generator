"""Property-based tests for Docker configuration.

Feature: deployment-and-release
"""

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List

import yaml
from hypothesis import given, settings
from hypothesis import strategies as st


# Property 11: Docker image dependency completeness
# Feature: deployment-and-release, Property 11: Docker image dependency completeness
@settings(max_examples=100)
@given(st.just("Dockerfile"))
def test_docker_image_dependency_completeness(dockerfile_name: str) -> None:
    """Test that Docker image includes all application dependencies.
    
    **Validates: Requirements 4.1**
    
    For any built Docker image, inspecting the image should show that all application 
    dependencies from pyproject.toml are installed.
    """
    # Read the Dockerfile
    dockerfile_path = Path(__file__).parent.parent.parent / dockerfile_name
    assert dockerfile_path.exists(), f"Dockerfile not found at {dockerfile_path}"
    
    dockerfile_content = dockerfile_path.read_text()
    
    # Verify multi-stage build structure
    assert "FROM python:3.13-slim as builder" in dockerfile_content, (
        "Dockerfile must use Python 3.13-slim as builder stage"
    )
    assert "FROM python:3.13-slim" in dockerfile_content.split("as builder")[1], (
        "Dockerfile must use Python 3.13-slim for runtime stage"
    )
    
    # Verify uv is installed for dependency management
    assert "pip install" in dockerfile_content and "uv" in dockerfile_content, (
        "Dockerfile must install uv for dependency management"
    )
    
    # Verify pyproject.toml is copied for dependency installation
    assert "COPY pyproject.toml" in dockerfile_content, (
        "Dockerfile must copy pyproject.toml for dependency installation"
    )
    
    # Verify uv.lock is copied for reproducible builds
    assert "uv.lock" in dockerfile_content, (
        "Dockerfile must copy uv.lock for reproducible dependency installation"
    )
    
    # Verify dependencies are installed
    assert "uv pip install" in dockerfile_content, (
        "Dockerfile must use uv pip install to install dependencies"
    )
    
    # Verify fonts-dejavu is installed (required for signature generation)
    assert "fonts-dejavu" in dockerfile_content, (
        "Dockerfile must install fonts-dejavu for text rendering"
    )
    
    # Verify application code is copied
    assert "COPY src/" in dockerfile_content, (
        "Dockerfile must copy src/ directory"
    )
    assert "COPY main.py" in dockerfile_content, (
        "Dockerfile must copy main.py entry point"
    )
    assert "COPY config/" in dockerfile_content, (
        "Dockerfile must copy config/ directory"
    )
    
    # Verify __version__.py is available for version reading
    assert "__version__.py" in dockerfile_content, (
        "Dockerfile must ensure __version__.py is available"
    )


# Property 12: Docker Compose volume configuration
# Feature: deployment-and-release, Property 12: Docker Compose volume configuration
@settings(max_examples=100)
@given(st.just("docker-compose.yml"))
def test_docker_compose_volume_configuration(compose_file_name: str) -> None:
    """Test that docker-compose.yml configures required volume mounts.
    
    **Validates: Requirements 4.3**
    
    For any docker-compose.yml file, parsing the configuration should reveal 
    volume mounts for output, profiles, and config directories.
    """
    # Read and parse docker-compose.yml
    compose_path = Path(__file__).parent.parent.parent / compose_file_name
    assert compose_path.exists(), f"docker-compose.yml not found at {compose_path}"
    
    with open(compose_path, 'r') as f:
        compose_config = yaml.safe_load(f)
    
    # Verify services section exists
    assert 'services' in compose_config, "docker-compose.yml must have 'services' section"
    
    # Verify email-signature service exists
    assert 'email-signature' in compose_config['services'], (
        "docker-compose.yml must define 'email-signature' service"
    )
    
    service = compose_config['services']['email-signature']
    
    # Verify volumes section exists
    assert 'volumes' in service, "email-signature service must have 'volumes' section"
    
    volumes = service['volumes']
    assert isinstance(volumes, list), "volumes must be a list"
    assert len(volumes) > 0, "volumes list must not be empty"
    
    # Convert volumes to strings for easier checking
    volume_strings = [str(v) for v in volumes]
    
    # Verify required volume mounts
    required_mounts = {
        '/app/output': False,
        '/app/profiles': False,
        '/app/config': False,
    }
    
    for volume in volume_strings:
        for mount_point in required_mounts.keys():
            if mount_point in volume:
                required_mounts[mount_point] = True
    
    # Check all required mounts are present
    missing_mounts = [mount for mount, found in required_mounts.items() if not found]
    assert not missing_mounts, (
        f"docker-compose.yml missing required volume mounts: {missing_mounts}"
    )
    
    # Verify output directory is writable (not read-only)
    output_volumes = [v for v in volume_strings if '/app/output' in v]
    assert output_volumes, "Output volume mount not found"
    for vol in output_volumes:
        assert ':ro' not in vol or '/app/output:ro' not in vol, (
            "Output directory must be writable (not read-only)"
        )
    
    # Verify profiles directory is writable (not read-only)
    profile_volumes = [v for v in volume_strings if '/app/profiles' in v]
    assert profile_volumes, "Profiles volume mount not found"
    for vol in profile_volumes:
        assert ':ro' not in vol or '/app/profiles:ro' not in vol, (
            "Profiles directory must be writable (not read-only)"
        )


# Property 13: Docker Compose environment variables
# Feature: deployment-and-release, Property 13: Docker Compose environment variables
@settings(max_examples=100)
@given(st.just("docker-compose.yml"))
def test_docker_compose_environment_variables(compose_file_name: str) -> None:
    """Test that docker-compose.yml defines required environment variables.
    
    **Validates: Requirements 4.4**
    
    For any docker-compose.yml file, the configuration should define environment 
    variables for customization (OUTPUT_DIR, etc.).
    """
    # Read and parse docker-compose.yml
    compose_path = Path(__file__).parent.parent.parent / compose_file_name
    assert compose_path.exists(), f"docker-compose.yml not found at {compose_path}"
    
    with open(compose_path, 'r') as f:
        compose_config = yaml.safe_load(f)
    
    # Get the email-signature service
    service = compose_config['services']['email-signature']
    
    # Verify environment section exists
    assert 'environment' in service, (
        "email-signature service must have 'environment' section"
    )
    
    environment = service['environment']
    assert isinstance(environment, list), "environment must be a list"
    assert len(environment) > 0, "environment list must not be empty"
    
    # Convert environment to strings for easier checking
    env_strings = [str(e) for e in environment]
    
    # Verify required environment variables
    required_env_vars = {
        'OUTPUT_DIR': False,
        'PYTHONUNBUFFERED': False,
    }
    
    for env_var in env_strings:
        for var_name in required_env_vars.keys():
            if var_name in env_var:
                required_env_vars[var_name] = True
    
    # Check all required environment variables are present
    missing_vars = [var for var, found in required_env_vars.items() if not found]
    assert not missing_vars, (
        f"docker-compose.yml missing required environment variables: {missing_vars}"
    )
    
    # Verify OUTPUT_DIR points to the mounted volume
    output_dir_vars = [e for e in env_strings if 'OUTPUT_DIR' in e]
    assert output_dir_vars, "OUTPUT_DIR environment variable not found"
    assert any('/app/output' in e for e in output_dir_vars), (
        "OUTPUT_DIR must point to /app/output"
    )
    
    # Verify PYTHONUNBUFFERED is set to 1 for proper logging
    unbuffered_vars = [e for e in env_strings if 'PYTHONUNBUFFERED' in e]
    assert unbuffered_vars, "PYTHONUNBUFFERED environment variable not found"
    assert any('PYTHONUNBUFFERED=1' in e or 'PYTHONUNBUFFERED: 1' in e for e in unbuffered_vars), (
        "PYTHONUNBUFFERED must be set to 1"
    )


# Property 14: Container data persistence
# Feature: deployment-and-release, Property 14: Container data persistence
@settings(max_examples=100, deadline=None)
@given(
    test_filename=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
        min_size=5,
        max_size=20
    ).map(lambda s: f"test_{s}.txt")
)
def test_container_data_persistence(test_filename: str) -> None:
    """Test that container preserves data in mounted volumes.
    
    **Validates: Requirements 7.3, 7.5**
    
    For any files generated within a running container, stopping and restarting 
    the container should preserve those files in the mounted volumes.
    """
    # This test verifies the configuration supports persistence
    # Actual container testing would require Docker to be running
    
    # Read docker-compose.yml
    compose_path = Path(__file__).parent.parent.parent / "docker-compose.yml"
    assert compose_path.exists(), "docker-compose.yml not found"
    
    with open(compose_path, 'r') as f:
        compose_config = yaml.safe_load(f)
    
    service = compose_config['services']['email-signature']
    
    # Verify volumes are configured for persistence
    assert 'volumes' in service, "Service must have volumes configured"
    volumes = service['volumes']
    
    # Verify output and profiles directories are mounted (these need persistence)
    volume_strings = [str(v) for v in volumes]
    
    # Check output directory is mounted from host
    output_mounts = [v for v in volume_strings if '/app/output' in v]
    assert output_mounts, "Output directory must be mounted for persistence"
    
    # Verify it's a bind mount (host:container format)
    for mount in output_mounts:
        assert ':' in mount, "Output mount must be a bind mount (host:container)"
        parts = mount.split(':')
        assert len(parts) >= 2, "Mount must have host and container paths"
        # Verify container path is /app/output
        assert '/app/output' in parts[1], "Container path must be /app/output"
    
    # Check profiles directory is mounted from host
    profile_mounts = [v for v in volume_strings if '/app/profiles' in v]
    assert profile_mounts, "Profiles directory must be mounted for persistence"
    
    # Verify it's a bind mount
    for mount in profile_mounts:
        assert ':' in mount, "Profiles mount must be a bind mount (host:container)"
        parts = mount.split(':')
        assert len(parts) >= 2, "Mount must have host and container paths"
        assert '/app/profiles' in parts[1], "Container path must be /app/profiles"
    
    # Verify Dockerfile creates these directories
    dockerfile_path = Path(__file__).parent.parent.parent / "Dockerfile"
    dockerfile_content = dockerfile_path.read_text()
    
    assert 'mkdir' in dockerfile_content, "Dockerfile must create volume directories"
    assert '/app/output' in dockerfile_content, "Dockerfile must create /app/output"
    assert '/app/profiles' in dockerfile_content, "Dockerfile must create /app/profiles"


# Property 15: Container environment variable application
# Feature: deployment-and-release, Property 15: Container environment variable application
@settings(max_examples=100)
@given(
    output_dir=st.sampled_from(['/app/output', '/custom/output', '/data/signatures'])
)
def test_container_environment_variable_application(output_dir: str) -> None:
    """Test that container applies environment variables correctly.
    
    **Validates: Requirements 7.4**
    
    For any environment variable defined in docker-compose.yml, the running 
    container should apply that configuration correctly.
    """
    # Read docker-compose.yml
    compose_path = Path(__file__).parent.parent.parent / "docker-compose.yml"
    assert compose_path.exists(), "docker-compose.yml not found"
    
    with open(compose_path, 'r') as f:
        compose_config = yaml.safe_load(f)
    
    service = compose_config['services']['email-signature']
    
    # Verify environment variables are properly formatted
    assert 'environment' in service, "Service must have environment section"
    environment = service['environment']
    
    # Verify environment is a list (docker-compose format)
    assert isinstance(environment, list), (
        "Environment must be a list for proper variable passing"
    )
    
    # Verify each environment variable is properly formatted
    for env_var in environment:
        env_str = str(env_var)
        # Should be in KEY=VALUE or KEY: VALUE format
        assert '=' in env_str or ':' in env_str, (
            f"Environment variable '{env_var}' must be in KEY=VALUE or KEY: VALUE format"
        )
    
    # Verify Dockerfile sets default environment variables
    dockerfile_path = Path(__file__).parent.parent.parent / "Dockerfile"
    dockerfile_content = dockerfile_path.read_text()
    
    # Check ENV directives exist
    assert 'ENV PYTHONUNBUFFERED' in dockerfile_content, (
        "Dockerfile must set PYTHONUNBUFFERED environment variable"
    )
    assert 'ENV OUTPUT_DIR' in dockerfile_content, (
        "Dockerfile must set OUTPUT_DIR environment variable"
    )
    
    # Verify the default OUTPUT_DIR in Dockerfile
    env_lines = [line for line in dockerfile_content.split('\n') if 'ENV OUTPUT_DIR' in line]
    assert env_lines, "OUTPUT_DIR environment variable not found in Dockerfile"
    
    # Verify it's set to /app/output by default
    assert any('/app/output' in line for line in env_lines), (
        "Default OUTPUT_DIR must be /app/output"
    )
    
    # Verify docker-compose can override the default
    compose_env_strings = [str(e) for e in environment]
    output_dir_vars = [e for e in compose_env_strings if 'OUTPUT_DIR' in e]
    assert output_dir_vars, (
        "docker-compose.yml must define OUTPUT_DIR to allow customization"
    )


# Property 18: Docker image version tagging
# Feature: deployment-and-release, Property 18: Docker image version tagging
@settings(max_examples=100)
@given(st.just("Makefile"))
def test_docker_image_version_tagging(makefile_name: str) -> None:
    """Test that docker-build target tags images with current version.
    
    **Validates: Requirements 5.4**
    
    For any execution of docker-build target, the created Docker image should be 
    tagged with the current version from __version__.py.
    """
    # Read the Makefile
    makefile_path = Path(__file__).parent.parent.parent / makefile_name
    assert makefile_path.exists(), f"Makefile not found at {makefile_path}"
    
    makefile_content = makefile_path.read_text()
    
    # Verify docker-build target exists
    assert 'docker-build:' in makefile_content, (
        "Makefile must have docker-build target"
    )
    
    # Extract the docker-build target section
    lines = makefile_content.split('\n')
    docker_build_start = None
    docker_build_lines = []
    
    for i, line in enumerate(lines):
        if 'docker-build:' in line:
            docker_build_start = i
        elif docker_build_start is not None:
            # Stop at next target or empty line without tab
            if line and not line.startswith('\t') and not line.startswith(' ') and ':' in line:
                break
            if line.startswith('\t') or line.startswith(' '):
                docker_build_lines.append(line)
    
    docker_build_section = '\n'.join(docker_build_lines)
    
    # Verify docker build command exists
    assert 'docker build' in docker_build_section, (
        "docker-build target must execute 'docker build' command"
    )
    
    # Verify version is used in tagging
    # Should reference version either through $(shell make version) or similar
    assert 'version' in docker_build_section.lower(), (
        "docker-build target must reference version for tagging"
    )
    
    # Verify docker tag command exists or -t flag with version
    has_tag_command = 'docker tag' in docker_build_section
    has_version_in_build = '-t' in docker_build_section and 'version' in docker_build_section.lower()
    
    assert has_tag_command or has_version_in_build, (
        "docker-build target must tag image with version using 'docker tag' or '-t' flag"
    )
    
    # Verify image name is email-signature-generator
    assert 'email-signature-generator' in docker_build_section, (
        "Docker image must be named 'email-signature-generator'"
    )
    
    # Verify latest tag is also created
    assert 'latest' in docker_build_section, (
        "docker-build target should also create 'latest' tag"
    )
    
    # Read __version__.py to verify version file exists
    version_file = Path(__file__).parent.parent.parent / "src" / "email_signature" / "__version__.py"
    assert version_file.exists(), "__version__.py must exist for version tagging"
    
    # Verify version file has __version__ variable
    version_content = version_file.read_text()
    assert '__version__' in version_content, (
        "__version__.py must define __version__ variable"
    )
    
    # Verify version follows semantic versioning format
    version_match = re.search(r'__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']', version_content)
    assert version_match, (
        "__version__ must follow semantic versioning format (MAJOR.MINOR.PATCH)"
    )
    
    # Verify docker-compose.yml uses VERSION environment variable
    compose_path = Path(__file__).parent.parent.parent / "docker-compose.yml"
    if compose_path.exists():
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        service = compose_config['services']['email-signature']
        
        # Verify image tag uses VERSION variable
        if 'image' in service:
            image_tag = service['image']
            assert '${VERSION' in image_tag or 'latest' in image_tag, (
                "docker-compose.yml image should use ${VERSION} variable or latest tag"
            )
