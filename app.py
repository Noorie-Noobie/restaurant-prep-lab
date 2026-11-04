import json
import altair as alt
import streamlit as st
from restaurant_lab.config import DB_PATH
from restaurant_lab.data import load_orders
from restaurant_lab.analytics import bestsellers, rush_hours
from restaurant_lab.meta_stock_ui import render_meta_stock
from restaurant_lab.planner_ui import render_planner

st.set_page_config(page_title='Restaurant Prep Lab', page_icon='🍕', layout='wide')
st.title('Restaurant Prep Lab')
page = st.sidebar.radio('Workspace', ['Explore','Prep Planner','Meta Evidence'])
st.caption('Fictional pizza restaurant • 2015 historical data • local times, timezone unspecified' if page == 'Explore' else 'Restaurant operations prototype • explicitly labeled demo inputs • no live restaurant data')
st.sidebar.caption('Synthetic demos • no live restaurant database. Meta requests require explicit opt-in and configured access.')
if page == 'Explore':
    if not DB_PATH.exists():
        st.info('Run: python -m restaurant_lab.data'); st.stop()
    lines = load_orders()
    dates = st.date_input('Order date range', value=(lines.ordered_at.min().date(), lines.ordered_at.max().date()))
    if len(dates) != 2: st.info('Choose an end date.'); st.stop()
    lines = lines[lines.ordered_at.dt.date.between(dates[0], dates[1])]
    if lines.empty: st.info('No orders in this range.'); st.stop()
    a,b,c = st.columns(3)
    a.metric('Orders', f'{lines.order_id.nunique():,}')
    b.metric('Pizzas sold', f'{lines.quantity.sum():,}')
    c.metric('Sales', f"${(lines.quantity*lines.unit_price_cents).sum()/100:,.2f}")
    st.subheader('What sells most?')
    ranking = bestsellers(lines)
    st.bar_chart(ranking.head(10).set_index('item_name')['units'])
    with st.expander('All dishes: units and revenue'):
        st.dataframe(ranking, hide_index=True)
    st.subheader('When is the rush?')
    st.caption('Distinct orders by weekday and local hour, total over selected dates. Unequal weekday coverage can affect comparisons; daily averages are task A2.')
    heat = rush_hours(lines).rename_axis('weekday').reset_index().melt(id_vars='weekday', var_name='hour', value_name='orders')
    st.altair_chart(alt.Chart(heat).mark_rect().encode(x=alt.X('hour:O', title='Local hour'), y=alt.Y('weekday:N', sort=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']), color=alt.Color('orders:Q', scale=alt.Scale(scheme='yelloworangered')), tooltip=['weekday','hour','orders']), width='stretch')
    st.caption('Revenue is sales, not profit. Customer identities and repeat visits are unavailable.')
elif page == 'Prep Planner':
    render_planner()
else:
    render_meta_stock()
