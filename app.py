import json
import altair as alt
import streamlit as st
from restaurant_lab.config import DB_PATH
from restaurant_lab.data import load_orders
from restaurant_lab.analytics import bestsellers, rush_hours, planning_menu
from restaurant_lab.meta import validate_extraction

st.set_page_config(page_title='Restaurant Prep Lab', page_icon='🍕', layout='wide')
st.title('Restaurant Prep Lab')
st.caption('Fictional pizza restaurant • 2015 historical data • local times, timezone unspecified')
page = st.sidebar.radio('Workspace', ['Explore','Prep Planner','Meta Evidence'])
st.sidebar.caption('Starter: no API requests, no cloud database, no live restaurant data.')
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
    st.subheader('Seven-dish planning scope')
    st.warning('Scaffold only: forecast and feasible prep calculation are not implemented yet.')
    if DB_PATH.exists(): st.dataframe(planning_menu(load_orders()), hide_index=True)
    st.write('Next: size-specific recipes → confirmed stock → demand baseline → ingredient/time checks → feasible prep quantities.')
    st.caption('The seven names are selected by full-dataset units, with alphabetical tie breaks. All sizes remain separate item IDs. Recipe amounts, stock, costs and capacity must be labeled demo assumptions.')
else:
    st.subheader('Meta Evidence · Muse Spark')
    st.info('Manual review rehearsal. No live model output has been generated.')
    st.write('Invoice photo → Muse Spark structured fields + source evidence → human correction → validated stock → deterministic planner → grounded explanation')
    st.file_uploader('Preview an invoice photo (kept in this session; not sent to Meta)', type=['png','jpg','jpeg'], key='photo')
    if st.session_state.photo: st.image(st.session_state.photo, width=500)
    st.caption('The adapter is in src/restaurant_lab/meta.py. Live-call controls, durable confirmation and planner handoff are teammate tasks M1–M4.')
    raw = st.text_area('Optional manual candidate JSON for validation (not model output)', value='{"ingredients": []}', height=150)
    if st.button('Validate manual candidate'):
        try:
            result = validate_extraction(json.loads(raw))
            st.json(result)
            st.success('Schema valid. Human confirmation and saving are still required; nothing written to inventory.')
        except Exception as exc: st.error(str(exc))
