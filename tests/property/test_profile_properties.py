"""Property-based tests for profile management."""

import tempfile
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from src.email_signature.domain.models import SignatureData
from src.email_signature.interface.gui.profile_manager import ProfileManager

# Strategy for generating non-empty strings with valid content
non_empty_string = st.text(min_size=1, max_size=100).filter(lambda s: s.strip())

# Strategy for generating valid profile names (alphanumeric with spaces, hyphens, underscores)
valid_profile_name = st.text(
    alphabet=st.characters(whitelist_categories=["Lu", "Ll", "Nd"], whitelist_characters=" -_"),
    min_size=1,
    max_size=50
).filter(lambda s: s.strip() and any(c.isalnum() for c in s))

# Strategy for generating valid email-like strings
valid_email = st.builds(
    lambda user, domain, tld: f"{user}@{domain}.{tld}",
    user=st.text(alphabet=st.characters(whitelist_categories=["Lu", "Ll", "Nd"]), min_size=1, max_size=20),
    domain=st.text(alphabet=st.characters(whitelist_categories=["Lu", "Ll", "Nd"]), min_size=1, max_size=20),
    tld=st.sampled_from(["com", "pt", "org", "net", "io"])
)

# Strategy for generating optional phone numbers (empty or valid format)
optional_phone = st.one_of(
    st.just(""),
    st.builds(
        lambda digits: f"+351 {digits[:3]} {digits[3:6]} {digits[6:9]}",
        digits=st.text(alphabet="0123456789", min_size=9, max_size=9)
    )
)


@given(
    profile_name=valid_profile_name,
    name=non_empty_string,
    position=non_empty_string,
    address=non_empty_string,
    phone=optional_phone,
    mobile=optional_phone,
    email=valid_email,
    website=st.text(min_size=1, max_size=100),
)
def test_profile_round_trip(
    profile_name: str,
    name: str,
    position: str,
    address: str,
    phone: str,
    mobile: str,
    email: str,
    website: str,
) -> None:
    """Feature: gui-interface, Property 10: Profile round-trip.
    
    Validates: Requirements 5.2, 5.4
    
    For any signature data, saving as a profile then loading that profile
    should restore all field values exactly.
    """
    # Create a temporary directory for profiles
    with tempfile.TemporaryDirectory() as temp_dir:
        profile_manager = ProfileManager(profiles_dir=temp_dir)
        
        # Create original signature data
        original_data = SignatureData(
            name=name,
            position=position,
            address=address,
            phone=phone,
            mobile=mobile,
            email=email,
            website=website,
        )
        
        # Save the profile
        profile_manager.save_profile(profile_name, original_data)
        
        # Load the profile back
        loaded_data = profile_manager.load_profile(profile_name)
        
        # Verify all fields match exactly
        assert loaded_data.name == original_data.name
        assert loaded_data.position == original_data.position
        assert loaded_data.address == original_data.address
        assert loaded_data.phone == original_data.phone
        assert loaded_data.mobile == original_data.mobile
        assert loaded_data.email == original_data.email
        assert loaded_data.website == original_data.website
