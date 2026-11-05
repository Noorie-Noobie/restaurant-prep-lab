"""Shared presentation only; business calculations remain in their existing modules."""
import altair as alt
import streamlit as st

TEAL = '#287052'
AMBER = '#d96a35'
INK = '#253e33'
MUTED = '#647064'


def apply_style():
    st.markdown('''<style>
    .stApp {background:#f7f1e5;color:#253e33;}
    [data-testid="stHeader"] {background:#f7f1e5;}
    [data-testid="stSidebar"] {background:#213e32;color:#f9f1df;border-right:0;min-width:230px;max-width:230px;}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label {color:#f9f1df!important;}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color:#c2ceba!important;}
    .block-container {padding:2.3rem 2rem 2rem;max-width:1500px;}
    h1 {font-family:Georgia,serif!important;font-size:2.7rem!important;line-height:1.12!important;letter-spacing:-.10rem;color:#213e32!important;max-width:900px;}
    h2 {font-family:Georgia,serif!important;font-size:2rem!important;}
    h3 {font-size:1.15rem!important;letter-spacing:-.02rem;}
    [data-testid="stMetric"] {border-left:4px solid #d96a35;padding:4px 18px 10px;margin:12px 0 20px;}
    [data-testid="stMetricValue"] {color:#213e32;font-family:Georgia,serif;font-size:clamp(1.5rem,2.4vw,2rem);font-weight:700;}
    [data-testid="stForm"] {background:#ebe3d1;border:1px solid #d4c5a9;border-radius:4px;}
    [data-testid="stVerticalBlockBorderWrapper"] > div {border-color:#dfd5c2;}
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {color:#58634f!important;}
    .eyebrow {display:inline-block;background:#ba4a2b;color:#fff7e9;font-size:.7rem;letter-spacing:.15rem;font-weight:700;padding:7px 12px;margin-bottom:12px;}
    .intro {color:#59634f;font-size:1rem;padding-bottom:20px;border-bottom:1px solid #d7c8ae;margin-bottom:18px;}
    .demo-tag {display:inline-block;border:1px solid #b2ad7a;color:#f3d18d;background:#304d3a;border-radius:3px;padding:6px 10px;font-size:.68rem;letter-spacing:.05rem;}
    .brand {font-family:Georgia,serif;font-size:2.1rem;color:#fff4d9;line-height:1.1;margin:0 0 12px;}
    .brand em {color:#ecad6c;}
    [data-testid="stFormSubmitButton"] button {background:#ba4a2b;color:#fff7e9;border:0;border-radius:4px;font-weight:700;}
    button:focus-visible {outline:3px solid #d96a35!important;}
    @media(max-width:760px){.block-container{padding:1.5rem 1rem;}h1{font-size:2.3rem!important;}[data-testid="stMetricValue"]{font-size:1.8rem;}}
    </style>''', unsafe_allow_html=True)


def chart_style(chart):
    return (chart.configure(background='#fffdf7')
        .configure_view(strokeWidth=0)
        .configure_axis(labelColor=MUTED,titleColor=MUTED,gridColor='#e4dccd',domain=False,
                        labelFontSize=12,titleFontSize=12,labelPadding=8,titlePadding=12)
        .configure_legend(labelColor=INK,titleColor=MUTED,labelFontSize=12,titleFontSize=12))


def heading(kicker, title, subtitle):
    # Call only with fixed application copy, not uploaded/model-generated text.
    st.markdown(f'<div class="eyebrow">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="intro">{subtitle}</div>', unsafe_allow_html=True)
