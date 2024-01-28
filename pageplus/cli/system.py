from pathlib import Path

import typer
from rich import print

app = typer.Typer()

@app.command()
def clean_logs() -> None:
    """
    Clean all log files.

    Returns:
    None
    """
    # Create a Path object for the directory
    path = Path(__file__).parents[2].joinpath('logs')
    print(path)
    # Iterate over all files in the directory
    for log_file in path.glob('*.log'):
        try:
            log_file.unlink()  # Delete the file
            print(f"Deleted log file: {log_file}")
        except OSError as e:
            print(f"Error: {e} - {log_file}")

if __name__ == "__main__":
    app()
