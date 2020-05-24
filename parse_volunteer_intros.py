from typing import Dict, Optional
import re

import pandas as pd

TEMPLATE_START = r"Greetings from <(@\w+)> :wave: (.*)"

# map fields used in 'loose' texts to keys in the official bot template
CUSTOM_KEYS = {
    "I know:": "Language(s) I speak",
    "I speak": "Language(s) I speak",
    "I live in": "I live in",
    "Live in": "I live in",
    "I am from": "I live in",
    "My top skills are": "My top skills are",
    "I am good at": "My top skills are",
    "I've joined because": "I've joined because",
    "My concern is": "I've joined because",
    "I'm NAME to": "I would like to help with"
}


def parse_bot_template(text: str) -> Optional[Dict[str, str]]:
    """
    Parse introduction texts that were generated using the welcome bots
    :param text: full Slack message text
    :return: field name -> field content dict
    """

    template_match = re.search(TEMPLATE_START, text)
    if not template_match:
        return None

    user_id = template_match.group(1)
    template_text = template_match.group(2)

    text_to_search = template_text
    fields = {
        "user_id": user_id,
        "uses_bot_template": True,
    }
    cur_field = None

    while True:
        field_match = re.search(r"\*(.+?):\*", text_to_search)
        if not field_match:
            break

        start_idx, end_idx = field_match.span()

        # parse value of previous field
        if cur_field:
            fields[cur_field] = text_to_search[:start_idx].strip()

        # parse key of current field
        cur_field = field_match.group(1)

        # remove text up until current field
        text_to_search = text_to_search[end_idx:]

    # parse remaining text as value of last field
    if cur_field:
        fields[cur_field] = text_to_search.strip()

    return fields


def parse_custom_text(text: str) -> Optional[Dict[str, str]]:
    """
    Try to parse information from text that the user structured themselves
    :param text: full Slack message text
    :return: field name -> field content dict (field names mapped to standard bot template)
    """

    fields = {
        "user_id": "UNKNOWN",
        "uses_bot_template": False
    }

    # pre-process text
    text = text.replace("*", "")

    for key in CUSTOM_KEYS:

        key_match = re.search(f"{key}:", text)
        if not key_match:
            continue
        start_idx, end_idx = key_match.span()
        text_after_key = text[end_idx:]

        value = ""
        for idx, char in enumerate(text_after_key):
            # check if we hit the next key
            if any(text_after_key[idx:].startswith(key + ":") for key in CUSTOM_KEYS):
                break
            value += char

        # clean the value
        value = value.strip("*").strip()

        # retrieve corresponding bot template key
        template_key = CUSTOM_KEYS[key]

        # field already filled: append
        if template_key in fields:
            fields[template_key] += " / " + value

        fields[template_key] = value

    return fields


def main():
    df = pd.read_csv("volunteer_long_form_responses.csv", names=["msg_id", "text"])

    parsed_templates = []

    for i, row in df.iterrows():
        bot_fields = parse_bot_template(row["text"])
        if bot_fields:
            if bot_fields.get("I live in") == "test":
                continue
            parsed_templates.append(bot_fields)
            continue

        custom_fields = parse_custom_text(row["text"])
        if len(custom_fields) > 2:
            parsed_templates.append(custom_fields)

    parsed_df = pd.DataFrame(parsed_templates)
    parsed_df.to_csv("volunteer_long_form_responses.parsed.csv")


if __name__ == '__main__':
    main()
