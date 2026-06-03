import subprocess


def main() -> None:
    subprocess.run(["ruff", "format"])
    subprocess.run(["ruff", "check", "--fix"])


if __name__ == "__main__":
    main()
