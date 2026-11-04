"""Fully synthetic 12-week fixture. No operational DB, network or real accuracy claim."""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import csv
import io
import json
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from restaurant_lab.imports import FIELDS, LocationConfig, preview_csv, commit_preview
from restaurant_lab.forecasting import MenuItem, forecast, backtest

CONFIG=LocationConfig('synthetic_forecast','demo','UTC','USD',4)
START=date(2026,6,1)

def build_demo(db, weeks=12):
    coverage={}
    for n in range(weeks*7):
        day=START+timedelta(days=n)
        qty=(10 if day.weekday()==0 else 4)+2*(n//7)
        ordered=datetime.combine(day,datetime.min.time(),timezone.utc)+timedelta(hours=12)
        closed=ordered.replace(hour=5)+timedelta(days=1)
        row=dict(zip(FIELDS,['1',CONFIG.source,CONFIG.location_id,str(n),'line','pizza-demo',
            'Synthetic demo item',ordered.isoformat(),ordered.isoformat(),'UTC',str(day),'USD',
            'each',str(qty),str(qty),'completed',str(qty*10),'0','0']))
        out=io.StringIO();writer=csv.DictWriter(out,fieldnames=FIELDS);writer.writeheader();writer.writerow(row)
        class Clock(datetime):
            @classmethod
            def now(cls,tz=None): return closed
        # Simulate historical ingestion ONLY inside this disposable synthetic fixture.
        with patch('restaurant_lab.imports.datetime',Clock):
            commit_preview(preview_csv(out.getvalue().encode(),CONFIG,db),confirmed=True)
        coverage[day]=closed
    menu=[MenuItem('pizza-demo','each',START,datetime(2026,5,31,tzinfo=timezone.utc))]
    return coverage,menu


def main():
    with TemporaryDirectory() as temp:
        db=Path(temp)/'synthetic.sqlite';coverage,menu=build_demo(db)
        target=START+timedelta(weeks=12)
        result=forecast(CONFIG,target=target,as_of=datetime.combine(target,datetime.min.time(),timezone.utc)+timedelta(hours=4),coverage=coverage,menu=menu,db_path=db)
        scored=backtest(CONFIG,targets=[START+timedelta(weeks=w) for w in range(8,12)],evaluation_as_of=datetime(2026,9,1,tzinfo=timezone.utc),coverage=coverage,menu=menu,db_path=db)
        print(json.dumps(dict(label='SYNTHETIC ONLY; designed trend, not real-world accuracy',forecast=result,backtest_metrics=scored['metrics']),indent=2))

if __name__=='__main__':main()
