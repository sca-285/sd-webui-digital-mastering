import launch

# Only what the extension imports. transformers usually comes with the host,
# so it is installed only when missing.
packages = [
    "transformers>=4.40.0",
    "accelerate",
    "safetensors",
    "pillow",
]

for package in packages:
    name = package.split("==")[0].split(">=")[0].split("<=")[0]
    if not launch.is_installed(name):
        launch.run_pip(f"install {package}", f"Digital Mastering requirement: {package}")
