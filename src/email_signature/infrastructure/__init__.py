"""Infrastructure layer - External dependencies (file I/O, image processing)."""

from .file_service import FileSystemError, FileSystemService
from .image_renderer import ImageRenderer, ImageRenderError
from .logo_loader import LogoLoader, LogoLoadError, LogoNotFoundError
from .platform_utils import (
    FontLocator,
    LineEndingHandler,
    PathManager,
    PlatformInfo,
    SystemCommandExecutor,
    TempFileManager,
    get_platform,
    is_linux,
    is_macos,
    is_virtual_env,
    is_windows,
)

__all__ = [
    "LogoLoader",
    "LogoLoadError",
    "LogoNotFoundError",
    "ImageRenderer",
    "ImageRenderError",
    "FileSystemService",
    "FileSystemError",
    "PathManager",
    "SystemCommandExecutor",
    "FontLocator",
    "TempFileManager",
    "LineEndingHandler",
    "PlatformInfo",
    "get_platform",
    "is_windows",
    "is_macos",
    "is_linux",
    "is_virtual_env",
]
