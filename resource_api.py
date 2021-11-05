"""Handling resource type API and grade them
(1) valid resource -- we could do this daily if we want to
    - create "uptime" record in `spice` and send stats update
    - calculate grade
(2) invalid resource - weekly should be fine.
    - update with F grade
"""
from resource import get_invalid_api_resources, get_valid_api_resources
from db import Database
from spice import (
    get_uptime_record_for,
    create_uptime_record,
    uptime_record_test,
    is_real_api,
)


db = Database()


def process_invalid_api_resources():
    """Grade these groups 'F' automatically since it's definitely NOT API"""
    fields = ["id", "package_id", "grade", "format", "url"]
    records = get_invalid_api_resources()
    cnt = 0
    for i in records:
        row = dict(zip(fields, i))
        if row["grade"] != "f":
            # update to F
            result = db.resource_grade_update(row["id"], "f")
            # print("result = ", result)
            cnt += 1

    print(f"Invalid resource updated total #{cnt}")
    return cnt


def process_api_resources():
    """Trickier situation since we need to call `spice` and check if there is any record. Then
    (1) create record if not exists
        - actually optional, but it is way easier to follow if uptime."group" is set
    (2) update stats
    """
    fields = ["id", "package_id", "grade", "name", "format", "url"]
    records = get_valid_api_resources()
    created, stats_update, no_record, bad = 0, 0, 0, 0
    for i in records:
        row = dict(zip(fields, i))
        url = row["url"]
        print(url)
        # check if it's real API?
        is_valid, ct = is_real_api(url)
        print(f"   > {'[ / ]' if is_valid else '[ X ]'} {ct}")
        if not is_valid:
            # update to F
            db.resource_grade_update(row["id"], "f")
            bad += 1
            continue
        elif row["grade"] == "f":  # is_valid now but currently is F grade.
            # update to null if resource turns out to be good
            db.resource_grade_update(row["id"], None)

        has_record = False
        status_code, _ = get_uptime_record_for(url)
        c = None
        if status_code == 404:
            # need to create a record
            c, _ = create_uptime_record(row["name"], row["url"])
            if c == 201:
                created += 1
                has_record = True
        elif status_code == 200:
            has_record = True

        if has_record:
            # get this uptime stats
            uptime_record_test(url)
            stats_update += 1
        else:
            print(" !!! no record: ", url, c)
            no_record += 1

        # if created > 10 or stats_update > 10:
        #     break

    print(
        f"API resource created #{created} stats update #{stats_update} bad #{bad} no record #{no_record}"
    )
    return {
        "created": created,
        "bad": bad,
        "stats_update": stats_update,
        "no_record": no_record,
    }


if __name__ == "__main__":
    process_invalid_api_resources()
    process_api_resources()
