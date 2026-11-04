"""User-confirmed synthetic operational walkthrough; no live writes or API calls."""
import streamlit as st
import pandas as pd
from .operations_demo import RECIPES, forecast_example
from .planning import plan_prep

@st.cache_data(show_spinner=False)
def _example():
    return forecast_example()


def render_planner():
    st.subheader('Anticipate demand → check stock → plan prep')
    st.warning('Synthetic operations demo: invented order history, fixed recipe and stock assumptions. Separate from the 2015 Explore dataset. No live restaurant data. Stock can optionally come from a human-reviewed Meta extraction of the synthetic note.')
    result=_example();item=result['items'][0]
    st.caption(f"Demo target: {result['target']} • UTC • prior four matching weekdays. Not a forecast for today.")
    if item['status']!='ready': st.info('Insufficient history. No prep recommendation.');return
    demand=-(-item['forecast_micros']//1000000)
    st.metric('Expected portions',demand)
    st.write('Prior comparable days: '+', '.join(str(q//1000000) for q in item['observed_fulfilled_micros']))
    st.bar_chart(pd.DataFrame({'Business date':item['observation_dates'],'Fulfilled portions':[q/1000000 for q in item['observed_fulfilled_micros']]}).set_index('Business date'))
    st.caption('Simple historical average, not a guarantee. Stockouts can hide unmet demand; no real accuracy claim.')
    st.subheader('Fixed recipe — one demo portion')
    st.write('250 g dough + 100 g cheese + 80 g sauce; 2 preparation minutes. These demo amounts never change when stock runs low.')
    audit=st.session_state.get('meta_confirmed_stock')
    if audit:
        st.caption('Stock initialized from human-reviewed Meta synthetic note. Request: '+audit['request_id']+'; subsequent edits are manual scenario changes.')
    for name,default in [('dough',10000.0),('cheese',2000.0),('sauce',3000.0)]:
        if 'stock_'+name not in st.session_state:st.session_state['stock_'+name]=default
    with st.form('stock_scenario'):
        st.subheader('Counted stock and preparation time')
        dough=st.number_input('Dough available (g)',min_value=0.0,max_value=1000000.0,step=250.0,key='stock_dough')
        cheese=st.number_input('Cheese available (g)',min_value=0.0,max_value=1000000.0,step=100.0,key='stock_cheese')
        sauce=st.number_input('Sauce available (g)',min_value=0.0,max_value=1000000.0,step=80.0,key='stock_sauce')
        minutes=st.number_input('Preparation time available (minutes)',min_value=0,max_value=10000,value=60,step=1)
        confirmed=st.checkbox('I reviewed these demo stock amounts and fixed recipe')
        calculate=st.form_submit_button('Calculate prep scenario')
    if not calculate:return
    if not confirmed:st.error('Review and confirm the demo inputs before calculating.');return
    plan=plan_prep({'pizza-demo':demand},RECIPES,{
        'dough':{'quantity':dough,'unit':'g'},'cheese':{'quantity':cheese,'unit':'g'},
        'sauce':{'quantity':sauce,'unit':'g'}},minutes)
    a,b,c=st.columns(3)
    a.metric('Feasible portions',plan['prepared']['pizza-demo'])
    b.metric('Unmet expected portions',plan['unmet']['pizza-demo'])
    c.metric('Preparation minutes used',plan['minutes_used'])
    st.dataframe(pd.DataFrame(plan['ingredients']).rename(columns={
        'required':'Required for full forecast','available':'Counted stock',
        'shortage':'Shortage for full forecast','remaining_after_prep':'Remaining after feasible prep'}),hide_index=True)
    if plan['unmet']['pizza-demo']:
        st.warning('Current resources cannot cover the expected portions. Review the ingredient shortages and time gap before service; keep the recipe fixed.')
    else: st.success('This scenario can cover the expected portions within the stated stock and preparation time.')
    st.write(f"Time needed for all expected portions: {plan['minutes_required']} minutes. Time gap: {plan['minutes_shortfall']} minutes.")
    st.info('Try a hypothetical replenishment: change cheese to 3,500 g and calculate again. This does not order ingredients or update saved inventory.')
    st.caption('Results describe the last submitted inputs. No inventory changes, purchases or automatic restaurant actions were made.')
