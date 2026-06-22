#!/usr/bin/env python3
"""
SYJ WebSense AI
Main CLI Application

Author: Syed Ali Hasan Moosavi
License: MIT
"""

from __future__ import annotations

import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from scraper import scrape_website
from ai_engine import WebSenseAI


console = Console()


APP_BANNER = r"""
╔══════════════════════════════════════════════════════╗
║                                                      ║
║   ███████╗██╗   ██╗     ██╗    ██╗███████╗██████╗    ║
║   ██╔════╝╚██╗ ██╔╝     ██║    ██║██╔════╝██╔══██╗   ║
║   ███████╗ ╚████╔╝      ██║ █╗ ██║█████╗  ██████╔╝   ║
║   ╚════██║  ╚██╔╝       ██║███╗██║██╔══╝  ██╔══██╗   ║
║   ███████║   ██║        ╚███╔███╔╝███████╗██████╔╝   ║
║   ╚══════╝   ╚═╝         ╚══╝╚══╝ ╚══════╝╚═════╝    ║
║                                                      ║
║               SYJ WebSense AI v1.0.0                ║
║          Open Source Website Q&A Chatbot            ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
"""


def print_banner():
    console.print(APP_BANNER, style="bold cyan")


def print_help():
    console.print(
        Panel.fit(
            "[bold green]Available Commands[/bold green]\n\n"
            "[cyan]!url[/cyan]    Change website\n"
            "[cyan]!clear[/cyan]  Clear conversation history\n"
            "[cyan]!quit[/cyan]   Exit application",
            title="Commands",
        )
    )


def select_provider():
    console.print(
        Panel.fit(
            "[1] Groq (llama3-8b-8192)\n"
            "[2] Gemini (gemini-1.5-flash)",
            title="AI Provider",
        )
    )

    while True:
        choice = Prompt.ask(
            "Select provider",
            default="1",
        )

        if choice == "1":
            return "groq"

        if choice == "2":
            return "gemini"

        console.print(
            "[red]Invalid selection.[/red]"
        )


def load_website():
    while True:

        url = Prompt.ask(
            "\nEnter website URL"
        ).strip()

        if not url:
            continue

        with console.status(
            "[bold green]Scraping website...",
            spinner="dots",
        ):
            try:
                website_data = scrape_website(url)

            except Exception as e:
                console.print(
                    f"[red]Error:[/red] {e}"
                )
                continue

        console.print(
            Panel.fit(
                f"[bold green]Website Loaded Successfully[/bold green]\n\n"
                f"[cyan]Title:[/cyan] {website_data['title']}\n"
                f"[cyan]Description:[/cyan] {website_data['description'][:250]}\n"
                f"[cyan]Word Count:[/cyan] {website_data['word_count']}\n"
                f"[cyan]Headings:[/cyan] {len(website_data['headings'])}\n"
                f"[cyan]Paragraphs:[/cyan] {len(website_data['paragraphs'])}",
                title="Website Information",
            )
        )

        return website_data


def answer_question(
    engine: WebSenseAI,
    website_data,
    question: str,
):
    with console.status(
        "[bold cyan]Thinking...",
        spinner="dots",
    ):

        answer = engine.ask(
            question,
            website_data,
        )

    console.print(
        Panel(
            Markdown(answer),
            title="WebSense AI",
            border_style="green",
        )
    )


def main():

    print_banner()

    provider = select_provider()

    try:
        ai = WebSenseAI(
            provider=provider
        )

    except Exception as e:
        console.print(
            f"[red]AI Initialization Failed:[/red] {e}"
        )
        sys.exit(1)

    print_help()

    website_data = load_website()

    console.print(
        "\n[bold green]Website Q&A Ready.[/bold green]"
    )

    while True:

        try:

            question = Prompt.ask(
                "\n[bold cyan]Ask"
            ).strip()

            if not question:
                continue

            if question.lower() == "!quit":

                console.print(
                    "\n[yellow]Goodbye![/yellow]"
                )

                break

            elif question.lower() == "!clear":

                ai.clear_history()

                console.print(
                    "[green]Conversation history cleared.[/green]"
                )

                continue

            elif question.lower() == "!url":

                ai.clear_history()

                website_data = load_website()

                console.print(
                    "[green]Website changed successfully.[/green]"
                )

                continue

            answer_question(
                ai,
                website_data,
                question,
            )

        except KeyboardInterrupt:

            console.print(
                "\n[yellow]Interrupted. Exiting...[/yellow]"
            )

            break

        except Exception as e:

            console.print(
                f"[red]Error:[/red] {e}"
            )


if __name__ == "__main__":
    main()
