"""All business numbers are computed in Python, never by the model."""
import pandas as pd
DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

def bestsellers(lines):
    work = lines[lines.status == 'completed'].copy()
    work['revenue_usd'] = work.quantity * work.unit_price_cents / 100
    return (work.groupby('item_name').agg(units=('quantity','sum'),
            revenue_usd=('revenue_usd','sum')).reset_index()
            .sort_values(['units','item_name'], ascending=[False,True]))

def rush_hours(lines):
    # Count orders once, not once per pizza. Source timezone is unspecified local.
    orders = lines[lines.status == 'completed'].drop_duplicates('order_id').copy()
    orders['weekday'] = orders.ordered_at.dt.day_name()
    orders['hour'] = orders.ordered_at.dt.hour
    return (orders.groupby(['weekday','hour']).size().unstack(fill_value=0)
            .reindex(index=DAYS, columns=range(24), fill_value=0).fillna(0).astype(int))

def planning_menu(lines):
    # Scope selection only: never use this whole-year selection for forecast evaluation.
    return bestsellers(lines).head(7)
