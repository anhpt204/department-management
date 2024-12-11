from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Get the current date
current_date = datetime(2024, 1, 5)

# Calculate the date for the same day in the prior month
prior_month_date = current_date - relativedelta(months=1)

# Get the day of the month for the prior month date
day_of_prior_month = prior_month_date.day

print("Day of the prior month:", prior_month_date)
