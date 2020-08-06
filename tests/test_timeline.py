import tempfile
from datetime import datetime, timedelta

from bassoon import timeline


def get_timeline():
    tl = timeline.Timeline()
    start_date = datetime(2000, 1, 1)
    periods = (
        ("p0", -5, 10),
        ("p1", 0, 10),
        ("p2", 4, 1),
        ("p3", 30, 21),
        ("p4", -20, 10),
    )
    for pe in periods:
        tl.periods.append(
            timeline.Period(
                pe[0],
                start_date=start_date + timedelta(pe[1]),
                period=timedelta(pe[2]),
            )
        )

    events = (("begining of t1", 3), ("end of an era", 25), (None, 0), ("event", -4))
    for ev in events:
        tl.events.append(timeline.Event(start_date + timedelta(ev[1]), ev[0]))
    return tl


def test_graph_save():
    tl = get_timeline()
    ax = tl.plot()
    ax.figure.savefig(tempfile.mktemp(suffix=".png"))
