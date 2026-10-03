from apps.found_reports.models import FoundReport


def reports_match(lost_report, found_report):
    if lost_report.category_id != found_report.category_id:
        return False

    if (
        lost_report.document_number
        and found_report.document_number
        and lost_report.document_number.lower()
        == found_report.document_number.lower()
    ):
        return True

    if (
        lost_report.name_on_document
        and found_report.name_on_document
        and lost_report.date_of_birth
        and found_report.date_of_birth
        and lost_report.name_on_document.lower()
        == found_report.name_on_document.lower()
        and lost_report.date_of_birth
        == found_report.date_of_birth
    ):
        return True

    return False


def find_matches(lost_report):
    found_reports = FoundReport.objects.filter(
        status=FoundReport.Status.AT_STATION
    )

    return [
        found_report
        for found_report in found_reports
        if reports_match(lost_report, found_report)
    ]