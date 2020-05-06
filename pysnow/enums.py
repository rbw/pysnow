from enum import Enum


class Order(Enum):
    asc = "ASC"
    desc = "DESC"


class Comparator(Enum):
    pass


class Equality(Comparator):
    eq = "="
    ne = "!="
    gt = ">"
    gte = ">="
    lt = "<"
    lte = "<="


class Boolean(Comparator):
    and_ = "^"
    or_ = "^OR"
    nq_ = "^NQ"


# Retrieved by inspecting the `ON` dropdown
class DateTimeOn(Enum):
    today = "Today@javascript:gs.beginningOfToday()@javascript:gs.endOfToday()"
    yesterday = (
        "Yesterday@javascript:gs.beginningOfYesterday()@javascript:gs.endOfYesterday()"
    )
    tomorrow = (
        "Tomorrow@javascript:gs.beginningOfTomorrow()@javascript:gs.endOfTomorrow()"
    )
    this_week = (
        "This week@javascript:gs.beginningOfThisWeek()@javascript:gs.endOfThisWeek()"
    )
    last_week = (
        "Last week@javascript:gs.beginningOfLastWeek()@javascript:gs.endOfLastWeek()"
    )
    next_week = (
        "Next week@javascript:gs.beginningOfNextWeek()@javascript:gs.endOfNextWeek()"
    )
    this_month = (
        "This month@javascript:gs.beginningOfThisMonth()@javascript:gs.endOfThisMonth()"
    )
    last_month = (
        "Last month@javascript:gs.beginningOfLastMonth()@javascript:gs.endOfLastMonth()"
    )
    next_month = (
        "Next month@javascript:gs.beginningOfNextMonth()@javascript:gs.endOfNextMonth()"
    )
    last_3_months = "Last 3 months@javascript:gs.beginningOfLast3Months()@javascript:gs.endOfLast3Months()"
    last_6_months = "Last 6 months@javascript:gs.beginningOfLast6Months()@javascript:gs.endOfLast6Months()"
    last_9_months = "Last 9 months@javascript:gs.beginningOfLast9Months()@javascript:gs.endOfLast9Months()"
    last_12_months = "Last 12 months@javascript:gs.beginningOfLast12Months()@javascript:gs.endOfLast12Months()"
    this_quarter = "This quarter@javascript:gs.beginningOfThisQuarter()@javascript:gs.endOfThisQuarter()"
    last_quarter = "Last quarter@javascript:gs.beginningOfLastQuarter()@javascript:gs.endOfLastQuarter()"
    last_2_quarters = "Last 2 quarters@javascript:gs.beginningOfLast2Quarters()@javascript:gs.endOfLast2Quarters()"
    next_quarter = "Next quarter@javascript:gs.beginningOfNextQuarter()@javascript:gs.endOfNextQuarter()"
    next_2_quarter = "Next 2 quarters@javascript:gs.beginningOfNext2Quarters()@javascript:gs.endOfNext2Quarters()"
    this_year = (
        "This year@javascript:gs.beginningOfThisYear()@javascript:gs.endOfThisYear()"
    )
    next_year = (
        "Next year@javascript:gs.beginningOfNextYear()@javascript:gs.endOfNextYear()"
    )
    last_yesr = (
        "Last year@javascript:gs.beginningOfLastYear()@javascript:gs.endOfLastYear()"
    )
    last_2_years = "Last 2 years@javascript:gs.beginningOfLast2Years()@javascript:gs.endOfLast2Years()"
    last_7_days = "Last 7 days@javascript:gs.beginningOfLast7Days()@javascript:gs.endOfLast7Days()"
    last_30_days = "Last 30 days@javascript:gs.beginningOfLast30Days()@javascript:gs.endOfLast30Days()"
    last_60_days = "Last 60 days@javascript:gs.beginningOfLast60Days()@javascript:gs.endOfLast60Days()"
    last_90_days = "Last 90 days@javascript:gs.beginningOfLast90Days()@javascript:gs.endOfLast90Days()"
    last_120_days = "Last 120 days@javascript:gs.beginningOfLast120Days()@javascript:gs.endOfLast120Days()"
    this_hour = "Current hour@javascript:gs.beginningOfCurrentHour()@javascript:gs.endOfCurrentHour()"
    last_hour = (
        "Last hour@javascript:gs.beginningOfLastHour()@javascript:gs.endOfLastHour()"
    )
    last_2_hours = "Last 2 hours@javascript:gs.beginningOfLast2Hours()@javascript:gs.endOfLast2Hours()"
    this_minute = "Current minute@javascript:gs.beginningOfCurrentMinute()@javascript:gs.endOfCurrentMinute()"
    last_minute = "Last minute@javascript:gs.beginningOfLastMinute()@javascript:gs.endOfLastMinute()"
    last_15_minutes = "Last 15 minutes@javascript:gs.beginningOfLast15Minutes()@javascript:gs.endOfLast15Minutes()"
    last_30_minutes = "Last 30 minutes@javascript:gs.beginningOfLast30Minutes()@javascript:gs.endOfLast30Minutes()"
    last_45_minutes = "Last 45 minutes@javascript:gs.beginningOfLast45Minutes()@javascript:gs.endOfLast45Minutes()"
    one_year_ago = "One year ago@javascript:gs.beginningOfOneYearAgo()@javascript:gs.endOfOneYearAgo()"


class RelativeEquality(Comparator):
    ee = "EE"
    eq = "EE"  # on
    gt = "GT"  # after
    gte = "GE"  # on or after
    lt = "LT"  # before
    lte = "LTE"  # on or before


class RelativeTimeWindows(Enum):
    minutes = "minute"
    hours = "hour"
    days = "dayofweek"
    months = "month"
    quarters = "quarter"
    years = "year"


class RelativeDirection(Enum):
    ago = "ago"
    ahead = "ahead"
