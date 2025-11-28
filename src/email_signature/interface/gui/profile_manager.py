"""Profile management for saving and loading signature data."""

import json

from src.email_signature.domain.models import SignatureData
from src.email_signature.infrastructure.platform_utils import PathManager


class ProfileManager:
    """Manages saving and loading signature data profiles.

    Profiles are stored as JSON files in a profiles directory.
    Each profile contains all the signature data fields.
    """

    def __init__(self, profiles_dir: str = "profiles") -> None:
        """Initialize the ProfileManager.

        Args:
            profiles_dir: Directory path where profiles will be stored
        """
        self.profiles_dir = PathManager.normalize(profiles_dir)
        PathManager.ensure_parent_dirs(self.profiles_dir / "dummy")  # Ensure the directory itself exists

    def save_profile(self, name: str, data: SignatureData) -> None:
        """Save signature data to a profile file.

        Args:
            name: Profile name (used as filename)
            data: SignatureData to save

        Raises:
            ValueError: If profile name is empty or invalid
            OSError: If file cannot be written
        """
        if not name or not name.strip():
            raise ValueError("Profile name cannot be empty")

        # Sanitize filename
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_name:
            raise ValueError("Profile name must contain valid characters")

        profile_path = PathManager.join(str(self.profiles_dir), f"{safe_name}.json")
        PathManager.ensure_parent_dirs(profile_path)

        # Convert SignatureData to dictionary
        profile_data = {
            "name": data.name,
            "position": data.position,
            "address": data.address,
            "phone": data.phone,
            "mobile": data.mobile,
            "email": data.email,
            "website": data.website,
        }

        # Write to JSON file
        with open(str(profile_path), 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)

    def load_profile(self, name: str) -> SignatureData:
        """Load signature data from a profile file.

        Args:
            name: Profile name (filename without extension)

        Returns:
            SignatureData loaded from the profile

        Raises:
            FileNotFoundError: If profile does not exist
            ValueError: If profile data is invalid
            json.JSONDecodeError: If profile file is not valid JSON
        """
        if not name or not name.strip():
            raise ValueError("Profile name cannot be empty")

        # Sanitize filename
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        profile_path = PathManager.join(str(self.profiles_dir), f"{safe_name}.json")

        if not PathManager.exists(profile_path):
            native_path = str(profile_path)
            raise FileNotFoundError(
                f"Profile '{name}' not found at '{native_path}'. "
                f"Available profiles: {', '.join(self.list_profiles()) or 'none'}"
            )

        # Read from JSON file
        with open(str(profile_path), encoding='utf-8') as f:
            profile_data = json.load(f)

        # Validate required fields
        required_fields = ["name", "position", "address", "email"]
        for field in required_fields:
            if field not in profile_data:
                raise ValueError(f"Profile is missing required field: {field}")

        # Create SignatureData with defaults for optional fields
        return SignatureData(
            name=profile_data["name"],
            position=profile_data["position"],
            address=profile_data["address"],
            phone=profile_data.get("phone", ""),
            mobile=profile_data.get("mobile", ""),
            email=profile_data["email"],
            website=profile_data.get("website", "www.example.com"),
        )

    def list_profiles(self) -> list[str]:
        """List all available profile names.

        Returns:
            List of profile names (without .json extension)
        """
        if not PathManager.exists(self.profiles_dir):
            return []

        profiles = []
        for profile_path in self.profiles_dir.glob("*.json"):
            profiles.append(profile_path.stem)

        return sorted(profiles)

    def delete_profile(self, name: str) -> None:
        """Delete a profile file.

        Args:
            name: Profile name (filename without extension)

        Raises:
            FileNotFoundError: If profile does not exist
            ValueError: If profile name is empty or invalid
        """
        if not name or not name.strip():
            raise ValueError("Profile name cannot be empty")

        # Sanitize filename
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        profile_path = PathManager.join(str(self.profiles_dir), f"{safe_name}.json")

        if not PathManager.exists(profile_path):
            native_path = str(profile_path)
            raise FileNotFoundError(
                f"Profile '{name}' not found at '{native_path}'. "
                f"Available profiles: {', '.join(self.list_profiles()) or 'none'}"
            )

        profile_path.unlink()
