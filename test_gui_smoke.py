#!/usr/bin/env python
"""
Automated smoke test for GUI components.
Tests that GUI can initialize without displaying windows.
"""

import sys
from pathlib import Path


def test_gui_imports():
    """Test that all GUI modules can be imported."""
    print("Testing GUI imports...")
    try:
        from src.email_signature.interface.gui.main_window import MainWindow, check_tkinter_available
        from src.email_signature.interface.gui.signature_tab import SignatureTab
        from src.email_signature.interface.gui.settings_tab import SettingsTab
        from src.email_signature.interface.gui.profile_manager import ProfileManager
        from src.email_signature.interface.gui.preview_generator import PreviewGenerator
        from src.email_signature.interface.gui.validation_mixin import ValidationMixin
        print("✅ All GUI modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_tkinter_available():
    """Test that Tkinter is available."""
    print("\nTesting Tkinter availability...")
    try:
        from src.email_signature.interface.gui.main_window import check_tkinter_available
        if check_tkinter_available():
            import tkinter
            print(f"✅ Tkinter is available (version {tkinter.TkVersion})")
            return True
        else:
            print("❌ Tkinter is not available")
            return False
    except Exception as e:
        print(f"❌ Tkinter check error: {e}")
        return False


def test_dependencies_initialization():
    """Test that dependencies can be initialized."""
    print("\nTesting dependency initialization...")
    try:
        from src.email_signature.domain.config import ConfigLoader
        from src.email_signature.domain.validators import InputValidator
        from src.email_signature.application.use_cases import GenerateSignatureUseCase
        from src.email_signature.infrastructure.file_service import FileSystemService
        from src.email_signature.infrastructure.image_renderer import ImageRenderer
        from src.email_signature.infrastructure.logo_loader import LogoLoader

        # Load config
        config_path = Path("config/default_config.yaml")
        if config_path.exists():
            config = ConfigLoader.load(str(config_path))
        else:
            config = ConfigLoader.load(None)

        # Create dependencies
        validator = InputValidator()
        logo_loader = LogoLoader(config.logo_search_paths)
        image_renderer = ImageRenderer(config)
        file_service = FileSystemService()
        use_case = GenerateSignatureUseCase(
            image_renderer=image_renderer,
            logo_loader=logo_loader,
            file_service=file_service,
            config=config,
        )

        print("✅ All dependencies initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Dependency initialization error: {e}")
        return False


def test_profile_manager():
    """Test ProfileManager basic functionality."""
    print("\nTesting ProfileManager...")
    try:
        from src.email_signature.interface.gui.profile_manager import ProfileManager
        from src.email_signature.domain.models import SignatureData

        pm = ProfileManager()
        
        # Test list profiles (should not crash even if empty)
        profiles = pm.list_profiles()
        print(f"  Found {len(profiles)} existing profiles")
        
        print("✅ ProfileManager works correctly")
        return True
    except Exception as e:
        print(f"❌ ProfileManager error: {e}")
        return False


def test_preview_generator():
    """Test PreviewGenerator initialization."""
    print("\nTesting PreviewGenerator...")
    try:
        from src.email_signature.interface.gui.preview_generator import PreviewGenerator
        from src.email_signature.domain.config import ConfigLoader
        from src.email_signature.application.use_cases import GenerateSignatureUseCase
        from src.email_signature.infrastructure.file_service import FileSystemService
        from src.email_signature.infrastructure.image_renderer import ImageRenderer
        from src.email_signature.infrastructure.logo_loader import LogoLoader

        config_path = Path("config/default_config.yaml")
        if config_path.exists():
            config = ConfigLoader.load(str(config_path))
        else:
            config = ConfigLoader.load(None)

        logo_loader = LogoLoader(config.logo_search_paths)
        image_renderer = ImageRenderer(config)
        file_service = FileSystemService()
        use_case = GenerateSignatureUseCase(
            image_renderer=image_renderer,
            logo_loader=logo_loader,
            file_service=file_service,
            config=config,
        )

        pg = PreviewGenerator(use_case)
        print("✅ PreviewGenerator initialized successfully")
        return True
    except Exception as e:
        print(f"❌ PreviewGenerator error: {e}")
        return False


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("GUI SMOKE TEST SUITE")
    print("=" * 60)
    
    results = []
    
    results.append(("GUI Imports", test_gui_imports()))
    results.append(("Tkinter Availability", test_tkinter_available()))
    results.append(("Dependencies", test_dependencies_initialization()))
    results.append(("ProfileManager", test_profile_manager()))
    results.append(("PreviewGenerator", test_preview_generator()))
    
    print("\n" + "=" * 60)
    print("SMOKE TEST RESULTS")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 60)
    if all_passed:
        print("✅ ALL SMOKE TESTS PASSED")
        print("\nThe GUI is ready for manual testing.")
        print("Run: python gui_main.py")
        return 0
    else:
        print("❌ SOME SMOKE TESTS FAILED")
        print("\nPlease fix the issues before manual testing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
