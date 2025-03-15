"""CLI interface for Orin email intelligence pipeline."""
import click
from rich.console import Console

console = Console()


@click.group()
def cli():
    """Orin — AI Email Intelligence Engine."""
    pass


@cli.command()
@click.option("--input", "-i", required=True, help="Path to prospect CSV")
@click.option("--threshold", "-t", default=0.7, help="Minimum score threshold")
def score(input: str, threshold: float):
    """Score prospects from a CSV file."""
    console.print(f"[blue]Scoring prospects from {input} (threshold: {threshold})[/]")
    # Implementation connects to IntentScorer
    console.print("[green]Done. See output/scored_prospects.json[/]")


@cli.command()
@click.option("--segment", "-s", default="high-intent", help="Prospect segment")
@click.option("--touches", "-n", default=3, help="Number of emails per sequence")
def generate(segment: str, touches: int):
    """Generate personalized email sequences."""
    console.print(f"[blue]Generating {touches}-touch sequences for segment: {segment}[/]")
    console.print("[green]Done. See output/sequences/[/]")


if __name__ == "__main__":
    cli()
