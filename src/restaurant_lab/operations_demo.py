"""Explicit synthetic demonstration, isolated from historical pizza/operational DBs."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import runpy
from .config import ROOT
from .forecasting import forecast

RECIPES={'pizza-demo': {'minutes':2,'ingredients':{
    'dough':{'quantity':250,'unit':'g'},
    'cheese':{'quantity':100,'unit':'g'},
    'sauce':{'quantity':80,'unit':'g'}}}}


def forecast_example():
    builder=runpy.run_path(str(ROOT/'scripts/demo_forecast.py'))
    with TemporaryDirectory() as folder:
        db=Path(folder)/'synthetic.sqlite'
        coverage,menu=builder['build_demo'](db)
        target=builder['START']+timedelta(weeks=12)
        result=forecast(builder['CONFIG'],target=target,
            as_of=datetime.combine(target,datetime.min.time(),timezone.utc)+timedelta(hours=4),
            coverage=coverage,menu=menu,db_path=db)
    return result
