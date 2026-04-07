from __future__ import annotations

import base64
import csv
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

import tomllib


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = ROOT / "pyproject.toml"


def _load_project_metadata() -> dict[str, object]:
    with PYPROJECT_PATH.open("rb") as file:
        data = tomllib.load(file)
    return data["project"]


def _normalized_distribution_name(name: str) -> str:
    return name.replace("-", "_")


def _dist_info_dir(project: dict[str, object]) -> str:
    name = _normalized_distribution_name(project["name"])
    version = project["version"]
    return f"{name}-{version}.dist-info"


def _metadata_contents(project: dict[str, object]) -> str:
    lines = [
        "Metadata-Version: 2.1",
        f"Name: {project['name']}",
        f"Version: {project['version']}",
        f"Summary: {project.get('description', '')}",
    ]
    requires_python = project.get("requires-python")
    if requires_python:
        lines.append(f"Requires-Python: {requires_python}")

    for requirement in project.get("dependencies", []):
        lines.append(f"Requires-Dist: {requirement}")

    optional_dependencies = project.get("optional-dependencies", {})
    for extra, requirements in optional_dependencies.items():
        lines.append(f"Provides-Extra: {extra}")
        for requirement in requirements:
            lines.append(f"Requires-Dist: {requirement}; extra == '{extra}'")

    lines.append("")
    return "\n".join(lines)


def _wheel_contents() -> str:
    return "\n".join(
        [
            "Wheel-Version: 1.0",
            "Generator: minimal_backend",
            "Root-Is-Purelib: true",
            "Tag: py3-none-any",
            "",
        ]
    )


def _pth_contents() -> str:
    return f"{ROOT / 'src'}\n"


def _record_line(path: str, content: bytes) -> tuple[str, str, str]:
    digest = hashlib.sha256(content).digest()
    encoded_digest = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return path, f"sha256={encoded_digest}", str(len(content))


def _build_wheel_file(wheel_directory: str) -> str:
    project = _load_project_metadata()
    dist_name = _normalized_distribution_name(project["name"])
    version = project["version"]
    wheel_name = f"{dist_name}-{version}-py3-none-any.whl"
    dist_info_dir = _dist_info_dir(project)
    wheel_path = Path(wheel_directory) / wheel_name

    pth_name = f"{dist_name}.pth"
    metadata_path = f"{dist_info_dir}/METADATA"
    wheel_metadata_path = f"{dist_info_dir}/WHEEL"
    record_path = f"{dist_info_dir}/RECORD"

    files: list[tuple[str, bytes]] = [
        (pth_name, _pth_contents().encode("utf-8")),
        (metadata_path, _metadata_contents(project).encode("utf-8")),
        (wheel_metadata_path, _wheel_contents().encode("utf-8")),
        ("{}/top_level.txt".format(dist_info_dir), b"elder_service\n"),
    ]

    records = [_record_line(path, content) for path, content in files]

    with TemporaryDirectory() as temp_dir:
        record_file = Path(temp_dir) / "RECORD"
        with record_file.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(records)
            writer.writerow((record_path, "", ""))

        with ZipFile(wheel_path, "w", compression=ZIP_DEFLATED) as wheel:
            for path, content in files:
                wheel.writestr(path, content)
            wheel.write(record_file, record_path)

    return wheel_name


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, object] | None = None,
    metadata_directory: str | None = None,
) -> str:
    return _build_wheel_file(wheel_directory)


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, object] | None = None,
    metadata_directory: str | None = None,
) -> str:
    return _build_wheel_file(wheel_directory)


def get_requires_for_build_wheel(
    config_settings: dict[str, object] | None = None,
) -> list[str]:
    return []


def get_requires_for_build_editable(
    config_settings: dict[str, object] | None = None,
) -> list[str]:
    return []


def prepare_metadata_for_build_wheel(
    metadata_directory: str,
    config_settings: dict[str, object] | None = None,
) -> str:
    return _prepare_metadata(metadata_directory)


def prepare_metadata_for_build_editable(
    metadata_directory: str,
    config_settings: dict[str, object] | None = None,
) -> str:
    return _prepare_metadata(metadata_directory)


def _prepare_metadata(metadata_directory: str) -> str:
    project = _load_project_metadata()
    dist_info_dir = Path(metadata_directory) / _dist_info_dir(project)
    dist_info_dir.mkdir(parents=True, exist_ok=True)
    (dist_info_dir / "METADATA").write_text(_metadata_contents(project), encoding="utf-8")
    (dist_info_dir / "WHEEL").write_text(_wheel_contents(), encoding="utf-8")
    (dist_info_dir / "top_level.txt").write_text("elder_service\n", encoding="utf-8")
    return dist_info_dir.name


def build_sdist(
    sdist_directory: str,
    config_settings: dict[str, object] | None = None,
) -> str:
    project = _load_project_metadata()
    dist_name = _normalized_distribution_name(project["name"])
    version = project["version"]
    archive_name = f"{dist_name}-{version}.tar.gz"
    archive_path = Path(sdist_directory) / archive_name
    archive_path.write_bytes(b"")
    return archive_name
