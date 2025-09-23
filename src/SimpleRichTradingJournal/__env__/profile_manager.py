"""Profile management functionality."""

from pathlib import Path
from logprise import logger

from . import _files


class ProfileManager:
    """Manages SRTJ profiles."""

    def __init__(self):
        self.profiles_home: Path | None = None
        self.profile_folder: Path | None = None
        self.profile_name: str = ""
        self._load_profiles_home()

    def _load_profiles_home(self):
        """Load profiles home directory."""
        try:
            with open(_files.profiles_home_path_file) as f:
                self.profiles_home = Path(f.read().strip())
                if not self.profiles_home.exists():
                    self._install_default()
        except FileNotFoundError:
            self._install_default()

    def _install_default(self):
        """Install default profile structure."""
        self.profiles_home = Path(_files.default_install_root) / _files.profiles_home_folder
        self.profiles_home.mkdir(parents=True, exist_ok=True)

        with open(_files.profiles_home_path_file, "w") as f:
            f.write(str(self.profiles_home))

        logger.info(f"Installed profiles to {self.profiles_home}")

    def load_profile(self, profile_name: str | None = None):
        """Load a specific profile."""
        if profile_name:
            self.profile_name = profile_name
            self.profile_folder = self.profiles_home / f"{_files.profile_prefix}{profile_name}"
        else:
            self.profile_folder = self.profiles_home

        if not self.profile_folder.exists():
            self._create_profile(self.profile_folder)

        return self.profile_folder

    def _create_profile(self, profile_path: Path):
        """Create a new profile."""
        profile_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (profile_path / _files.folder_profile_assets).mkdir(exist_ok=True)
        (profile_path / _files.folder_profile_assets / _files.folder_file_clones).mkdir(exist_ok=True)
        (profile_path / _files.folder_trash).mkdir(exist_ok=True)

        # Create initial files
        (profile_path / _files.file_clean_time).write_text(str(int(time.time())))

        logger.info(f"Created profile at {profile_path}")

    def list_profiles(self) -> list[str]:
        """List all available profiles."""
        if not self.profiles_home:
            return []
        return [p.name for p in self.profiles_home.iterdir()
                if p.name.startswith(_files.profile_prefix)]


profile_manager = ProfileManager()