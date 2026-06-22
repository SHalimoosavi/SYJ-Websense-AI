#!/usr/bin/env python3
"""
SYJ WebSense AI
AI Engine Module

Author: Syed Ali Hasan Moosavi
License: MIT
"""

from __future__ import annotations

import os
from collections import deque
from typing import Dict, List

from dotenv import load_dotenv

load_dotenv()


class WebSenseAI:
    """
    WebSense AI Chat Engine

    Supports:
    - Groq
    - Google Gemini

    Maintains:
    - 5 turn conversation history
    - Website context
    """

    def __init__(self, provider: str = "groq"):
        self.provider = provider.lower()
        self.history = deque(maxlen=5)

        if self.provider == "groq":
            self._init_groq()

        elif self.provider == "gemini":
            self._init_gemini()

        else:
            raise ValueError(
                "Unsupported provider. Use 'groq' or 'gemini'."
            )

    # --------------------------------------------------
    # Provider Initialization
    # --------------------------------------------------

    def _init_groq(self):
        try:
            from groq import Groq

            api_key = os.getenv("GROQ_API_KEY")

            if not api_key:
                raise ValueError(
                    "GROQ_API_KEY not found in .env"
                )

            self.client = Groq(api_key=api_key)

        except ImportError:
            raise ImportError(
                "groq package not installed. "
                "Run: pip install groq"
            )

    def _init_gemini(self):
        try:
            import google.generativeai as genai

            api_key = os.getenv("GEMINI_API_KEY")

            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY not found in .env"
                )

            genai.configure(api_key=api_key)

            self.model = genai.GenerativeModel(
                "gemini-1.5-flash"
            )

        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Run: pip install google-generativeai"
            )

    # --------------------------------------------------
    # Context Handling
    # --------------------------------------------------

    def _build_website_context(
        self,
        website_data: Dict
    ) -> str:
        """
        Convert scraped website content
        into structured AI context.
        """

        title = website_data.get("title", "")
        description = website_data.get("description", "")

        headings = "\n".join(
            f"- {h}"
            for h in website_data.get("headings", [])
        )

        paragraphs = "\n".join(
            website_data.get("paragraphs", [])
        )

        context = f"""
WEBSITE TITLE:
{title}

META DESCRIPTION:
{description}

HEADINGS:
{headings}

CONTENT:
{paragraphs}
"""

        return context.strip()

    def _truncate_context(
        self,
        text: str,
        max_words: int = 4500,
    ) -> str:
        """
        Rough token control.

        4500 words ~= < 6000 tokens
        """

        words = text.split()

        if len(words) <= max_words:
            return text

        return " ".join(words[:max_words])

    def clear_history(self):
        """
        Reset conversation history.
        """
        self.history.clear()

    # --------------------------------------------------
    # Prompt Builder
    # --------------------------------------------------

    def _build_messages(
        self,
        question: str,
        website_data: Dict,
    ):
        """
        Build structured messages.
        """

        website_context = self._build_website_context(
            website_data
        )

        website_context = self._truncate_context(
            website_context
        )

        system_prompt = (
            "You are WebSense AI. "
            "Answer questions strictly using the provided website content. "
            "If the answer cannot be found in the website content, "
            "respond with: "
            "'The website does not provide enough information to answer that question.' "
            "Do not invent information."
        )

        history_text = ""

        for item in self.history:
            history_text += (
                f"User: {item['user']}\n"
                f"Assistant: {item['assistant']}\n\n"
            )

        user_message = f"""
WEBSITE CONTEXT
================
{website_context}

CONVERSATION HISTORY
====================
{history_text}

CURRENT QUESTION
================
{question}
"""

        return system_prompt, user_message

    # --------------------------------------------------
    # Groq
    # --------------------------------------------------

    def _ask_groq(
        self,
        question: str,
        website_data: Dict,
    ) -> str:

        system_prompt, user_message = (
            self._build_messages(
                question,
                website_data
            )
        )

        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            temperature=0.2,
            max_tokens=1024,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
        )

        answer = (
            response.choices[0]
            .message.content
            .strip()
        )

        self.history.append(
            {
                "user": question,
                "assistant": answer,
            }
        )

        return answer

    # --------------------------------------------------
    # Gemini
    # --------------------------------------------------

    def _ask_gemini(
        self,
        question: str,
        website_data: Dict,
    ) -> str:

        system_prompt, user_message = (
            self._build_messages(
                question,
                website_data
            )
        )

        final_prompt = f"""
{system_prompt}

{user_message}
"""

        response = self.model.generate_content(
            final_prompt
        )

        answer = response.text.strip()

        self.history.append(
            {
                "user": question,
                "assistant": answer,
            }
        )

        return answer

    # --------------------------------------------------
    # Public Interface
    # --------------------------------------------------

    def ask(
        self,
        question: str,
        website_data: Dict,
    ) -> str:
        """
        Ask WebSense AI a question.
        """

        if self.provider == "groq":
            return self._ask_groq(
                question,
                website_data,
            )

        return self._ask_gemini(
            question,
            website_data,
        )


if __name__ == "__main__":

    sample_site = {
        "title": "Example Website",
        "description": "Demo site",
        "headings": [
            "Welcome",
            "About Us"
        ],
        "paragraphs": [
            "This website provides example content."
        ],
        "word_count": 10,
    }

    engine = WebSenseAI(
        provider="groq"
    )

    while True:
        q = input("\nQuestion: ").strip()

        if q.lower() == "quit":
            break

        try:
            result = engine.ask(
                q,
                sample_site
            )

            print("\nAnswer:\n")
            print(result)

        except Exception as e:
            print(f"\nError: {e}")
