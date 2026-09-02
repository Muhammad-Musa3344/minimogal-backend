# app/content/founder_stories.py
# Fixed lookup table — Alina Morse / Zolli Candy story (S5 in the PRD).
# No AI, no DB call — just a static list the frontend fetches directly.

LOLLIPOP_STAND_FOUNDER_STORY = [
    {
        "card_id": 1,
        "title": "The Spark",
        "screen_text": "When Alina was 7, a bank teller offered her a lollipop. Her dad said no; candy is bad for your teeth.",
        "audio_text": "When Alina was just seven years old, a bank teller offered her a lollipop as a treat. Her dad said no — candy like that is bad for your teeth, he told her.",
    },
    {
        "card_id": 2,
        "title": "The Start",
        "screen_text": "Alina wondered: why isn't there a lollipop that's actually GOOD for you? So she started making her own.",
        "audio_text": "That got Alina thinking — why isn't there a lollipop that's actually good for you? So she decided to start making her own, right in her kitchen.",
    },
    {
        "card_id": 3,
        "title": "The Struggle",
        "screen_text": "Alina was just a kid. Getting stores to sell her lollipops wasn't easy.",
        "audio_text": "Alina was just a kid, and getting stores to take her seriously and sell her lollipops wasn't easy at all.",
    },
    {
        "card_id": 4,
        "title": "The Scale",
        "screen_text": "Today, Alina's lollipops sell in thousands of stores around the world.",
        "audio_text": "Today, Alina's lollipops sell in thousands of stores all around the world — and she even got invited to the White House.",
    },
]

def get_founder_story(business: str) -> list:
    """Returns the fixed founder-story flashcard sequence for a business.
    Currently only Lollipop Stand exists for Level 1."""
    stories = {
        "lollipop_stand": LOLLIPOP_STAND_FOUNDER_STORY,
    }
    return stories.get(business, [])