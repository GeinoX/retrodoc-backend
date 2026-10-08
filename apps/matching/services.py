from apps.found_reports.models import FoundReport
from apps.lost_reports.models import LostReport
from apps.matching.matching import reports_match


def find_matches(lost_report):
    found_reports = FoundReport.objects.filter(
        status=FoundReport.Status.AT_STATION
    )

    return [
        found_report
        for found_report in found_reports
        if reports_match(lost_report, found_report)
    ]


def apply_match(lost_report, found_report):
    lost_report.matched_found_report = found_report
    lost_report.status = LostReport.Status.POSSIBLE_MATCH

    lost_report.save(
        update_fields=[
            "matched_found_report",
            "status",
            "updated_at",
        ]
    )

    if found_report.status == FoundReport.Status.AT_STATION:
        found_report.status = FoundReport.Status.OWNER_MAY_BE_FOUND

        found_report.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    return lost_report