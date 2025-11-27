"""Unit tests for Docker configuration logo references.

Feature: data-sanitization
Example 5: Docker configurations reference correct logo
Validates: Requirements 3.3
"""

from pathlib import Path

import yaml


def test_dockerfile_references_logo_png() -> None:
    """Verify that Dockerfile COPY command references logo.png correctly.
    
    **Example 5: Docker configurations reference correct logo**
    **Validates: Requirements 3.3**
    
    This test verifies that:
    1. Dockerfile contains a COPY command for logo.png
    2. The logo is copied to the correct location in the container
    3. The logo filename is exactly "logo.png" (the generic placeholder)
    """
    # Given the Dockerfile in the repository root
    dockerfile_path = Path(__file__).parent.parent.parent / "Dockerfile"
    assert dockerfile_path.exists(), "Dockerfile not found"
    
    # When reading the Dockerfile content
    dockerfile_content = dockerfile_path.read_text()
    
    # Then it should contain a COPY command for logo.png
    assert "COPY logo.png" in dockerfile_content, (
        "Dockerfile must contain 'COPY logo.png' command"
    )
    
    # And it should copy to the application directory
    assert "COPY logo.png ./" in dockerfile_content or "COPY logo.png /app/" in dockerfile_content, (
        "Dockerfile must copy logo.png to the application directory"
    )
    
    # Verify the exact filename is logo.png (not any other logo file)
    lines = dockerfile_content.split('\n')
    logo_copy_lines = [line for line in lines if 'COPY' in line and 'logo' in line.lower()]
    
    assert logo_copy_lines, "No COPY command found for logo file"
    
    for line in logo_copy_lines:
        # Ensure it's specifically logo.png, not logo.jpg or other variants
        assert 'logo.png' in line, (
            f"Logo COPY command should reference 'logo.png', found: {line}"
        )


def test_docker_compose_references_logo_png() -> None:
    """Verify that docker-compose.yml volume mount references logo.png correctly.
    
    **Example 5: Docker configurations reference correct logo**
    **Validates: Requirements 3.3**
    
    This test verifies that:
    1. docker-compose.yml contains a volume mount for logo.png
    2. The volume mount uses the correct filename (logo.png)
    3. The volume mount is configured as read-only
    4. The container path is correct
    """
    # Given the docker-compose.yml in the repository root
    compose_path = Path(__file__).parent.parent.parent / "docker-compose.yml"
    assert compose_path.exists(), "docker-compose.yml not found"
    
    # When reading and parsing the docker-compose.yml
    with open(compose_path, 'r') as f:
        compose_config = yaml.safe_load(f)
    
    # Then it should have the email-signature service
    assert 'services' in compose_config, "docker-compose.yml must have 'services' section"
    assert 'email-signature' in compose_config['services'], (
        "docker-compose.yml must define 'email-signature' service"
    )
    
    service = compose_config['services']['email-signature']
    
    # And the service should have volumes configured
    assert 'volumes' in service, "email-signature service must have 'volumes' section"
    
    volumes = service['volumes']
    volume_strings = [str(v) for v in volumes]
    
    # And one of the volumes should mount logo.png
    logo_volumes = [v for v in volume_strings if 'logo.png' in v]
    assert logo_volumes, (
        "docker-compose.yml must include a volume mount for logo.png"
    )
    
    # Verify the volume mount format
    for logo_volume in logo_volumes:
        # Should be in format: ./logo.png:/app/logo.png:ro
        assert ':' in logo_volume, (
            f"Logo volume mount must use bind mount format (host:container), found: {logo_volume}"
        )
        
        parts = logo_volume.split(':')
        assert len(parts) >= 2, (
            f"Logo volume mount must have at least host and container paths, found: {logo_volume}"
        )
        
        # Verify host path references logo.png
        host_path = parts[0]
        assert 'logo.png' in host_path, (
            f"Host path must reference logo.png, found: {host_path}"
        )
        
        # Verify container path is /app/logo.png
        container_path = parts[1]
        assert '/app/logo.png' in container_path, (
            f"Container path must be /app/logo.png, found: {container_path}"
        )
        
        # Verify it's mounted as read-only
        if len(parts) >= 3:
            mount_options = parts[2]
            assert 'ro' in mount_options, (
                f"Logo should be mounted as read-only (:ro), found: {logo_volume}"
            )


def test_docker_configurations_use_consistent_logo_filename() -> None:
    """Verify that both Docker configurations use the same logo filename.
    
    **Example 5: Docker configurations reference correct logo**
    **Validates: Requirements 3.3**
    
    This test ensures consistency between Dockerfile and docker-compose.yml
    in their references to the logo file.
    """
    # Given both Docker configuration files
    dockerfile_path = Path(__file__).parent.parent.parent / "Dockerfile"
    compose_path = Path(__file__).parent.parent.parent / "docker-compose.yml"
    
    assert dockerfile_path.exists(), "Dockerfile not found"
    assert compose_path.exists(), "docker-compose.yml not found"
    
    # When reading both configurations
    dockerfile_content = dockerfile_path.read_text()
    
    with open(compose_path, 'r') as f:
        compose_config = yaml.safe_load(f)
    
    # Then both should reference exactly "logo.png"
    # Extract logo filename from Dockerfile
    dockerfile_logo_lines = [
        line for line in dockerfile_content.split('\n') 
        if 'COPY' in line and 'logo' in line.lower()
    ]
    
    assert dockerfile_logo_lines, "Dockerfile must have COPY command for logo"
    
    # All logo references in Dockerfile should be logo.png
    for line in dockerfile_logo_lines:
        assert 'logo.png' in line, (
            f"Dockerfile should reference 'logo.png', found: {line}"
        )
    
    # Extract logo filename from docker-compose.yml
    service = compose_config['services']['email-signature']
    volumes = service['volumes']
    volume_strings = [str(v) for v in volumes]
    
    logo_volumes = [v for v in volume_strings if 'logo' in v.lower()]
    assert logo_volumes, "docker-compose.yml must have volume mount for logo"
    
    # All logo references in docker-compose.yml should be logo.png
    for volume in logo_volumes:
        assert 'logo.png' in volume, (
            f"docker-compose.yml should reference 'logo.png', found: {volume}"
        )
    
    # Both configurations should use the exact same filename
    # This ensures consistency and prevents issues with mismatched filenames
