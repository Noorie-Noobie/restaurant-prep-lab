"""User-confirmed synthetic operational walkthrough; no live writes or API calls."""
import streamlit as st
import pandas as pd
import altair as alt
from .presentation import heading, chart_style, TEAL, AMBER, INK
from .operations_demo import RECIPES, forecast_example
from .planning import plan_prep

@st.cache_data(show_spinner=False)
def _example():
    return forecast_example()


def render_planner():
    heading('02 / PREP BEFORE SERVICE', 'Go into service with a plan.',
            'One question before opening: can your stock and prep time cover demand?')
    st.caption('SYNTHETIC SCENARIO · One demo pizza, invented history and stock. Separate from Explore; no live inventory changes.')
    result=_example();item=result['items'][0]
    if item['status']!='ready': st.info('Insufficient history. No prep recommendation.');return
    demand=-(-item['forecast_micros']//1000000)
    summary, history=st.columns([1,2],gap='large')
    with summary:
        st.subheader('1 · Anticipate demand')
        st.metric('Expected portions',demand)
        st.caption(f"Demo service: {result['target']} · UTC")
        st.write('The average of four comparable Mondays.')
        with st.expander('Forecast assumptions'):
            st.caption('Simple fulfilled-sales average, not a guarantee or a forecast for today. Stockouts can hide unmet demand. Only history known at the cutoff is used; no real accuracy claim.')
    with history:
        history_data=pd.DataFrame({'Date':item['observation_dates'],'Portions':[q/1000000 for q in item['observed_fulfilled_micros']]})
        base=alt.Chart(history_data).encode(x=alt.X('Date:O',title=None,axis=alt.Axis(labelAngle=0)),y=alt.Y('Portions:Q',scale=alt.Scale(domain=[0,40]),title='Portions sold'),tooltip=['Date','Portions'])
        bars=base.mark_bar(color='#dca269',cornerRadiusEnd=5,size=42)
        labels=base.mark_text(dy=-10,color=INK,fontSize=14).encode(text='Portions:Q')
        rule=alt.Chart(pd.DataFrame({'Expected':[demand]})).mark_rule(color=TEAL,strokeDash=[6,4],strokeWidth=2).encode(y='Expected:Q')
        st.altair_chart(chart_style((bars+labels+rule).properties(height=180)),width='stretch')
        st.caption('Bars = prior Mondays · green dashed line = 29 expected portions')
    st.subheader('2 · Check your resources')
    st.caption('FIXED RECIPE / PORTION · 250 g dough + 100 g cheese + 80 g sauce · 2 prep minutes. The recipe never changes to hide a shortage.')
    audit=st.session_state.get('meta_confirmed_stock')
    if audit:
        st.caption('Stock initialized from human-reviewed Meta synthetic note. Request: '+audit['request_id']+'; subsequent edits are manual scenario changes.')
    # Widget keys are cleaned up when their screen disappears. Keep committed
    # scenario inputs separately, and apply each reviewed Meta handoff once.
    if 'planner_stock_values' not in st.session_state:
        st.session_state['planner_stock_values']=(
            {name:float(value['quantity']) for name,value in audit['stock'].items()}
            if audit else {'dough':10000.0,'cheese':2000.0,'sauce':3000.0})
    revision=st.session_state.get('planner_stock_revision')
    new_handoff=revision != st.session_state.get('planner_widget_revision')
    for name,value in st.session_state['planner_stock_values'].items():
        if new_handoff or 'stock_'+name not in st.session_state:
            st.session_state['stock_'+name]=value
    st.session_state['planner_widget_revision']=revision
    with st.form('stock_scenario'):
        fields=st.columns(4)
        with fields[0]:
            dough=st.number_input('Dough available (g)',min_value=0.0,max_value=1000000.0,step=250.0,key='stock_dough')
        with fields[1]:
            cheese=st.number_input('Cheese available (g)',min_value=0.0,max_value=1000000.0,step=100.0,key='stock_cheese')
        with fields[2]:
            sauce=st.number_input('Sauce available (g)',min_value=0.0,max_value=1000000.0,step=80.0,key='stock_sauce')
        with fields[3]:
            minutes=st.number_input('Prep time (minutes)',min_value=0,max_value=10000,value=60,step=1)
        confirmed=st.checkbox('I reviewed these demo stock amounts and fixed recipe')
        calculate=st.form_submit_button('Calculate prep scenario')
    if not calculate:return
    st.session_state['planner_stock_values']={'dough':dough,'cheese':cheese,'sauce':sauce}
    if not confirmed:st.error('Review and confirm the demo inputs before calculating.');return
    plan=plan_prep({'pizza-demo':demand},RECIPES,{
        'dough':{'quantity':dough,'unit':'g'},'cheese':{'quantity':cheese,'unit':'g'},
        'sauce':{'quantity':sauce,'unit':'g'}},minutes)
    st.subheader('3 · Your prep scenario')
    a,b,c=st.columns(3)
    a.metric('Feasible portions',plan['prepared']['pizza-demo'])
    b.metric('Unmet expected portions',plan['unmet']['pizza-demo'])
    c.metric('Preparation minutes used',plan['minutes_used'])
    prepared=plan['prepared']['pizza-demo']
    if plan['unmet']['pizza-demo']:
        shortages=[f"{float(r['shortage']):g} {r['unit']} {r['ingredient']}" for r in plan['ingredients'] if float(r['shortage'])>0]
        gap=' + '.join(shortages)
        if float(plan['minutes_shortfall'])>0:
            gap += ('; ' if gap else '')+f"{plan['minutes_shortfall']} more prep minutes"
        st.warning(f"{prepared} of {demand} portions covered. To cover the full forecast, the scenario needs {gap}.")
    else:
        st.success(f"All {demand} expected portions are covered by this stock and time scenario.")
    comparison=[]
    for row in plan['ingredients']:
        comparison.extend([{'Ingredient':row['ingredient'].title(),'Amount (g)':float(row[key]),'Measure':label}
                           for key,label in [('available','Counted stock'),('required','Needed for forecast')]])
    st.subheader('Stock vs. what the full forecast needs')
    compare=alt.Chart(pd.DataFrame(comparison)).mark_bar(cornerRadiusEnd=4).encode(
        y=alt.Y('Ingredient:N',title=None,axis=alt.Axis(labelOverlap=False),scale=alt.Scale(paddingInner=0.3)),yOffset='Measure:N',
        x=alt.X('Amount (g):Q',title='Grams',scale=alt.Scale(zero=True)),
        color=alt.Color('Measure:N',scale=alt.Scale(domain=['Counted stock','Needed for forecast'],range=[TEAL,AMBER]),legend=alt.Legend(orient='top',title=None)),
        tooltip=['Ingredient','Measure',alt.Tooltip('Amount (g):Q',format=',')])
    st.altair_chart(chart_style(compare.properties(height=220)),width='stretch')
    st.caption(f"Full forecast needs {plan['minutes_required']} prep minutes; you entered {plan['minutes_available']}. Results reflect the submitted inputs.")
    with st.expander('Exact ingredient calculations'):
        st.dataframe(pd.DataFrame(plan['ingredients']).rename(columns={'required':'Needed for forecast','available':'Counted stock','shortage':'Shortage','remaining_after_prep':'Left after feasible prep'}),hide_index=True)
    st.info('Try the comparison: enter 3,500 g cheese above and calculate again. This is hypothetical replenishment, not an order or saved inventory change.')
