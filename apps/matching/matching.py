import re
import unicodedata


def normalize_text(value):
    if not value:
        return ""

    value = str(value).strip().lower()

    value = unicodedata.normalize("NFKD", value)
    value = "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )

    value = re.sub(r"[^a-z0-9]+", " ", value)

    return " ".join(value.split())


def normalize_document_number(value):
    if not value:
        return ""

    return re.sub(
        r"[^a-z0-9]",
        "",
        str(value).strip().lower(),
    )


def reports_match(lost_report, found_report):
    if lost_report.category_id != found_report.category_id:
        return False

    lost_number = normalize_document_number(
        lost_report.document_number
    )
    found_number = normalize_document_number(
        found_report.document_number
    )

    if (
        lost_number
        and found_number
        and lost_number == found_number
    ):
        return True

    lost_name = normalize_text(
        lost_report.name_on_document
    )
    found_name = normalize_text(
        found_report.name_on_document
    )

    if (
        lost_name
        and found_name
        and lost_report.date_of_birth
        and found_report.date_of_birth
        and lost_name == found_name
        and lost_report.date_of_birth
        == found_report.date_of_birth
    ):
        return True

    return False