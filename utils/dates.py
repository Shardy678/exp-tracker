from datetime import date
from dateutil.relativedelta import relativedelta

def month_range(today: date) -> tuple[date, date]:
    month_start = today.replace(day=1)
    month_end = (month_start + relativedelta(months=1)) - relativedelta(days=1)
    return month_start, month_end
