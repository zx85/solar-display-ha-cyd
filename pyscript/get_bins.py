# Bin lookup script
# This uses the Waste Collection Schedule HACS integration:
# https://ha.mus-ic.co.uk/hacs/repository/254347436
# And once the Calendar is setup, it looks up the bins for tomorrow and creates
# a sensor concatenating the first 2 letters of the bin colour (e.g. bk for
# black, bu for blue, br for brown)

import datetime

# lower case and just the colour
bin_lookup = {
    "black": "bk",
    "blue": "bu",
    "brown": "br",
    "green": "gr",
}


@service
# if it's "set" - look for tomorrow's bins (runs hourly between 3-9pm)
# otherwise clear the bins (normally scheduled at 12pm)
# (this is because the calendar doesn't show today's events if they're all-day)
def get_bins(status=None):
    if status != "set":
        log.info("Clearing bins.")
        state.set(
            "sensor.upcoming_bins", value=0, bins="", target_date="", mode="clear"
        )
        return
    # let's get tomorrow's bins
    now = datetime.datetime.now()
    target_date = now + datetime.timedelta(days=1)
    target_str = target_date.strftime("%Y-%m-%d")
    bin_list = ""
    bin_qty = 0

    # Fetch events from the calendar
    # We fetch a 2-day window to ensure we catch the relevant events
    result = calendar.get_events(
        entity_id="calendar.west_suffolk_council",
        start_date_time=now,
        end_date_time=now + datetime.timedelta(days=2),
    )

    events = result.get("calendar.west_suffolk_council", {}).get("events")
    log.info(f"Events is {events}")

    # Filter for all-day events matching our target date
    for event in events:
        start = event.get("start", {})
        # All-day events use the 'date' key instead of 'dateTime'
        if summary := event.get("summary"):
            bin_name = summary.lower().split(" ")[0]
            if start == target_str:
                bin_list = f'{bin_list}{bin_lookup.get(bin_name,"")}'
                bin_qty += 1

    # 4. Update a sensor so you can use this in your dashboard
    state.set(
        "sensor.upcoming_bins",
        value=bin_qty,
        bins=bin_list,
        target_date=target_str,
        mode="ready",
    )
