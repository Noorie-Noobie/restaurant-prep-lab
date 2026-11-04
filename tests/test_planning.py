from copy import deepcopy
from decimal import Decimal
import pytest
from streamlit.testing.v1 import AppTest
from restaurant_lab.config import ROOT
from restaurant_lab.operations_demo import RECIPES, forecast_example
from restaurant_lab.planning import plan_prep


def stock(cheese=2000):
    return {'dough':{'quantity':10000,'unit':'g'},'cheese':{'quantity':cheese,'unit':'g'},'sauce':{'quantity':3000,'unit':'g'}}


def test_forecast_to_shortage_and_replenishment():
    forecast=forecast_example()['items'][0]
    assert forecast['forecast_micros']==29000000
    recipes=deepcopy(RECIPES);inventory=stock()
    result=plan_prep({'pizza-demo':29},recipes,inventory,60)
    assert result['prepared']=={'pizza-demo':20} and result['unmet']=={'pizza-demo':9}
    cheese=next(r for r in result['ingredients'] if r['ingredient']=='cheese')
    assert cheese['shortage']=='900' and result['minutes_used']=='40'
    assert inventory==stock() and recipes==RECIPES
    result=plan_prep({'pizza-demo':29},recipes,stock(3500),60)
    assert result['prepared']=={'pizza-demo':29} and result['minutes_used']=='58'
    assert all(Decimal(r['remaining_after_prep'])>=0 for r in result['ingredients'])


def test_time_limit_zero_stock_and_unit_conversion():
    assert plan_prep({'pizza-demo':29},RECIPES,stock(3500),10)['prepared']['pizza-demo']==5
    assert plan_prep({'pizza-demo':29},RECIPES,stock(0),60)['prepared']['pizza-demo']==0
    inventory=stock();inventory['cheese']={'quantity':'2','unit':'kg'}
    assert plan_prep({'pizza-demo':29},RECIPES,inventory,60)['prepared']['pizza-demo']==20
    inventory['cheese']['unit']='ml'
    with pytest.raises(ValueError):plan_prep({'pizza-demo':29},RECIPES,inventory,60)


@pytest.mark.parametrize('bad',[-1,True,float('nan'),float('inf'),'oops','0.0000001'])
def test_invalid_inventory_rejected(bad):
    with pytest.raises(ValueError):plan_prep({'pizza-demo':29},RECIPES,stock(bad),60)


def test_missing_recipe_stock_and_fractional_portions():
    with pytest.raises(ValueError):plan_prep({'unknown':1},RECIPES,stock(),60)
    with pytest.raises(ValueError):plan_prep({'pizza-demo':1},RECIPES,{},60)
    with pytest.raises(ValueError):plan_prep({'pizza-demo':1.5},RECIPES,stock(),60)


def test_shared_ingredient_never_double_allocated():
    recipes={'b':RECIPES['pizza-demo'],'a':RECIPES['pizza-demo']}
    result=plan_prep({'b':20,'a':20},recipes,stock(),100)
    assert result['prepared']=={'a':20,'b':0}
    assert all(Decimal(r['remaining_after_prep'])>=0 for r in result['ingredients'])


def test_ui_confirmation_and_two_scenarios():
    app=AppTest.from_file(ROOT/'app.py').run(timeout=30)
    app.sidebar.radio[0].set_value('Prep Planner').run(timeout=30)
    assert not app.exception and app.metric[0].value=='29'
    app.button[0].click().run()
    assert 'confirm' in app.error[0].value
    app.checkbox[0].check()
    app.button[0].click().run()
    assert [m.value for m in app.metric]==['29','20','9','40']
    app.number_input[1].set_value(3500)
    app.button[0].click().run()
    assert [m.value for m in app.metric]==['29','29','0','58']
    assert not app.exception
