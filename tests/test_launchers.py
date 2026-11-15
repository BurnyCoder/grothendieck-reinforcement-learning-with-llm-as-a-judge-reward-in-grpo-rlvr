"""Exercise the user-facing WSL launcher without importing or running a model."""
import shutil
import subprocess

import pytest

from grothendieck_rlvr.io import PROJECT


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_launcher_preserves_paths_with_either_env_line_ending(tmp_path, newline):
    """Windows-edited configuration must not introduce CR bytes into Linux paths."""
    if shutil.which("bash") is None:
        pytest.skip("WSL launcher requires Bash")
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for source in (PROJECT / "scripts").glob("*.sh"):
        shutil.copy2(source, scripts / source.name)
    runtime = tmp_path / "native environment"
    interpreter = runtime / "bin/python"
    interpreter.parent.mkdir(parents=True)
    interpreter.write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$UNSLOTH_COMPILE_LOCATION"\n')
    interpreter.chmod(0o755)
    cache = tmp_path / "compiler cache"
    configuration = f"UV_PROJECT_ENVIRONMENT='{runtime}'\nUNSLOTH_COMPILE_LOCATION='{cache}'\n"
    (tmp_path / ".env").write_bytes(configuration.replace("\n", newline).encode())
    result = subprocess.run(["bash", str(scripts / "run.sh"), "doctor"], cwd=tmp_path,
                            capture_output=True, text=True, check=True)
    assert result.stdout == f"{cache}\n"
