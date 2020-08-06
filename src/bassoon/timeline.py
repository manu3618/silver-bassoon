"""
Tools to plot a timeline chart
"""
from datetime import datetime, timedelta

import pandas as pd
from matplotlib.cm import rainbow
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle


class Event:
    def __init__(self, date=None, label=None):
        if date is None:
            date = self.date = datetime.now()
        self.date = date

        if label is None:
            self.label = "Event of " + date.isoformat()

        self.label = label

    def __le__(self, value):
        return self.date.__le__(value.date)

    def __lt__(self, value):
        return self.date.__lt__(value.date)

    def __eq__(self, value):
        return self.date == value.date and self.label == value.label

    def __repr__(self):
        return "<Event {} ({})>".format(self.label[:8], str(self.date))


class Period:
    def __init__(self, label=None, start_date=None, end_date=None, period=None):
        if start_date is None:
            start_date = datetime.now()
        if end_date is not None and period is not None:
            raise ValueError("Cannot take both end_date and period")
        if end_date is None and period is None:
            period = timedelta(1)
        if end_date is None and period is not None:
            end_date = start_date + period
        if end_date < start_date:
            raise ValueError("end must be posterior to start.")
        if label is None:
            label = "Period from {} to {}".format(
                start_date.isoformat(), end_date.isoformat()
            )

        self.start = Event(start_date, "start of " + label)
        self.end = Event(end_date, "end of " + label)
        self.label = label

    def overlap(self, value):
        """Test if periods overlap

        Args:
            value (Period)
        Returns:
            bool
        """
        if self.end < value.start or value.end < self.start:
            return False
        return True

    def timelen(self):
        return self.end.date - self.end.date

    def __lt__(self, value):
        return self.start < value.start

    def __le__(self, value):
        return self.start <= value.start

    def __eq__(self, value):
        return self.start == value.start and self.end == value.end

    def __repr__(self):
        return "<Period {}>".format(self.label)


class Timeline:
    def __init__(self, periods=None):
        if periods is not None:
            self.periods = periods
        else:
            self.periods = []
        self.events = []

    def non_overlapping_periods(self):
        """Separate Periods in list of non overlapping periods

        Each returned list can be draw in a single line
        """
        self.periods.sort()
        non_overlapping = [[]]
        for period in self.periods:
            for period_list in non_overlapping:
                if any(p.overlap(period) for p in period_list):
                    continue
                else:
                    candidate = period_list
                    break
            else:
                candidate = []
                non_overlapping.append(candidate)
            candidate.append(period)
        return non_overlapping

    def _all_events(self):
        evs = [p.start for p in self.periods]
        evs.extend([p.end for p in self.periods])
        evs.extend(self.events)
        return evs

    def limits(self):
        evs = self._all_events()
        return min(evs), max(evs)

    def timelen(self):
        start, end = self.limits()
        return end.date - start.date

    def plot(self, cmap=rainbow):
        """Plot a timeline

        Returns:
            matplotlib.Axes
        """
        line_nb = len(self.non_overlapping_periods())
        evs = self._all_events()
        ax = pd.Series({ev.date: line_nb for ev in evs}).plot(alpha=0)
        corresp = dict(zip(ax.lines[0]._xorig, ax.lines[0]._x))

        for line, periods in enumerate(self.non_overlapping_periods()):
            for p_nb, period in enumerate(periods):
                x_lim = corresp[period.start.date], corresp[period.end.date]
                ax.add_patch(
                    Rectangle(
                        (x_lim[0], line),
                        x_lim[1] - x_lim[0],
                        1,
                        facecolor=cmap(line + p_nb),
                    )
                )
                ax.text(x_lim[0] + 0.1, line + 0.1, period.label)

        for event in self.events:
            xevent = corresp[event.date]
            ax.add_line(Line2D([xevent, xevent], [0, line_nb],))
            ax.text(xevent, line_nb + 0.5, event.label, rotation=45)

        return ax
