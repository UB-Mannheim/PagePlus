import typer

from pageplus.cli import (analytics, export, modification, projects, system,
                          validation)

app = typer.Typer()
app.add_typer(system.app, name="system")
app.add_typer(analytics.app, name="analytics")
app.add_typer(validation.app, name="validation")
app.add_typer(modification.app, name="modification")
app.add_typer(projects.app, name="projects")
app.add_typer(export.app, name="export")

if __name__ == "__main__":
    app()
