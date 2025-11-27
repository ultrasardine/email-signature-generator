"""Domain models for email signature generation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SignatureData:
    """Immutable data model for signature information.

    Attributes:
        name: User's full name (required)
        position: Job title/position (required)
        address: Physical address (required)
        phone: Landline phone number (optional)
        mobile: Mobile phone number (optional)
        email: Email address (required)
        website: Company website (defaults to "www.eos.pt")
    """

    name: str
    position: str
    address: str
    phone: str
    mobile: str
    email: str
    website: str = "www.eos.pt"

    def __post_init__(self) -> None:
        """Validate data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Name is required and cannot be empty")
        if not self.position or not self.position.strip():
            raise ValueError("Position is required and cannot be empty")
        if not self.address or not self.address.strip():
            raise ValueError("Address is required and cannot be empty")
        if not self.email or not self.email.strip():
            raise ValueError("Email is required and cannot be empty")
