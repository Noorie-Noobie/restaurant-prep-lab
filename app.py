import altair as alt
import streamlit as st
from restaurant_lab.config import DB_PATH
from restaurant_lab.data import load_orders
from restaurant_lab.analytics import bestsellers, rush_hours, DAYS
from restaurant_lab.meta_stock_ui import render_meta_stock
from restaurant_lab.planner_ui import render_planner
from restaurant_lab.presentation import apply_style, heading, chart_style, TEAL, AMBER, INK

st.set_page_config(page_title='Restaurant Prep Lab', page_icon='🍕', layout='wide')
apply_style()
st.sidebar.markdown('<div class="brand">Prep Lab<em>.</em></div>', unsafe_allow_html=True)
st.sidebar.caption('Restaurant operations, one service at a time.')
page = st.sidebar.radio('Workspace', ['Explore','Prep Planner','Meta Evidence'])
st.sidebar.divider()
st.sidebar.markdown('**The demo path**\n\n1. Understand past orders\n2. Check the prep plan\n3. Review Meta evidence')
st.sidebar.markdown('<span class="demo-tag">SYNTHETIC / FICTIONAL DATA</span>', unsafe_allow_html=True)
st.sidebar.caption('No live restaurant connected. Meta requires configured access and your explicit consent.')
if page == 'Explore':
    heading('01 / SALES PATTERNS', 'A clearer view of your next service.',
            'Start with the patterns: what guests order, and when your kitchen gets busy.')
    if not DB_PATH.exists():
        st.info('Run: python -m restaurant_lab.data'); st.stop()
    lines = load_orders()
    filter_col, label_col = st.columns([1.4,2])
    with filter_col:
        dates = st.date_input('Order date range', value=(lines.ordered_at.min().date(), lines.ordered_at.max().date()))
    with label_col:
        st.caption('DEMO SOURCE · Fictional pizza restaurant, 2015\n\nAll charts use the selected dates. Local clock times; source timezone unknown.')
    if len(dates) != 2: st.info('Choose an end date to update the charts.'); st.stop()
    lines = lines[lines.ordered_at.dt.date.between(dates[0], dates[1])]
    if lines.empty: st.info('No orders in this range. Choose dates within the 2015 sample.'); st.stop()
    a,b,c = st.columns([1,1,1.4])
    a.metric('Orders', f'{lines.order_id.nunique():,}')
    b.metric('Pizzas sold', f'{lines.quantity.sum():,}')
    c.metric('Sales', f"${(lines.quantity*lines.unit_price_cents).sum()/100:,.2f}")
    ranking = bestsellers(lines)
    # Presentation names only; preserve source identifiers and calculations.
    names={'classic_dlx':'Classic Deluxe','bbq_ckn':'BBQ Chicken','thai_ckn':'Thai Chicken','cali_ckn':'California Chicken','southw_ckn':'Southwest Chicken','big_meat':'Big Meat'}
    ranking['dish']=ranking.item_name.map(lambda x:names.get(x,x.replace('_',' ').title()))
    heat = rush_hours(lines).rename_axis('weekday').reset_index().melt(id_vars='weekday', var_name='hour', value_name='orders')
    peak = heat.loc[heat.orders.idxmax()]
    left,right=st.columns([1,1.15],gap='large')
    with left, st.container(border=True):
        st.subheader('01  /  Menu favourites')
        leader=ranking.iloc[0]
        st.caption(f"{leader.dish} leads with {leader.units:,} pizzas. Top 7 shown; sizes combined.")
        top=ranking.head(7)
        bars=alt.Chart(top).encode(y=alt.Y('dish:N',sort='-x',title=None,axis=alt.Axis(labelLimit=185)),
            x=alt.X('units:Q',title='Pizzas sold',scale=alt.Scale(domain=[0,int(top.units.max()*1.3)])),
            tooltip=[alt.Tooltip('dish:N',title='Dish'),alt.Tooltip('units:Q',title='Pizzas',format=',')])
        chart=bars.mark_bar(cornerRadiusEnd=5,size=22).encode(color=alt.condition(alt.datum.dish==leader.dish,alt.value(TEAL),alt.value('#dca269')))
        labels=bars.mark_text(align='left',dx=7,color=INK,fontSize=12).encode(text=alt.Text('units:Q',format=','))
        st.altair_chart(chart_style((chart+labels).properties(height=290)),width='stretch')
    with right, st.container(border=True):
        st.subheader('02  /  Service rhythm')
        st.caption(f"Peak cell: {peak.weekday}, {int(peak.hour):02d}:00–{int(peak.hour)+1:02d}:00 · {int(peak.orders):,} orders across selected dates.")
        active=heat.groupby('hour').orders.sum();hours=active[active>0].index
        visible=heat[heat.hour.between(int(hours.min()),int(hours.max()))].copy()
        visible['Day']=visible.weekday.str[:3]
        visible['Time']=visible.hour.map(lambda h:f'{h%12 or 12}{"a" if h<12 else "p"}')
        hour_order=[f'{h%12 or 12}{"a" if h<12 else "p"}' for h in range(int(hours.min()),int(hours.max())+1)]
        chart=alt.Chart(visible).mark_rect(cornerRadius=3,stroke='#fffdf7',strokeWidth=3).encode(
            x=alt.X('Time:O',sort=hour_order,title='Local hour',axis=alt.Axis(labelAngle=0,labelFontSize=11)),
            y=alt.Y('Day:N',sort=[d[:3] for d in DAYS],title=None),
            color=alt.Color('orders:Q',title='Orders',scale=alt.Scale(range=['#f4e5cc','#b64a28']),legend=alt.Legend(orient='bottom',gradientLength=160)),
            tooltip=[alt.Tooltip('weekday:N',title='Day'),alt.Tooltip('Time:N',title='Hour starting'),alt.Tooltip('orders:Q',title='Total orders',format=',')])
        st.altair_chart(chart_style(chart.properties(height=290)),width='stretch')
        st.caption('Deeper orange = more orders. Totals, not an average week; weekday coverage can differ. Hours with no orders anywhere in the selection are omitted at the edges.')
    with st.expander('See all dishes & understand the data'):
        st.dataframe(ranking.rename(columns={'item_name':'Dish','units':'Pizzas sold','revenue_usd':'Sales (USD)'}),hide_index=True)
        st.caption('Revenue is sales, not profit. Customer identities and repeat visits are unavailable. Missing dates are not assumed to be open with zero orders. Prep Planner uses a separate synthetic scenario, not a forecast fitted to this chart.')
elif page == 'Prep Planner':
    render_planner()
else:
    heading('03 / REVIEW THE EVIDENCE','Turn a stock note into checked inputs.',
            'Meta extracts the amounts. You review them before they reach the prep plan.')
    render_meta_stock()
