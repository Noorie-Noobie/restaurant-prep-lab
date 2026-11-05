import streamlit as st
from .meta_stock import NOTE, readiness, extract_demo_stock, candidate_grams, confirm_stock


def render_meta_stock():
    st.subheader('Meta Evidence — counted stock to prep inputs')
    st.info('Synthetic-only integration. No live result is shown until an actual Meta request succeeds. Existing invoice-image adapter remains separate and unverified.')
    st.code(NOTE,language=None)
    state=readiness()
    st.caption(f"Meta Model API · muse-spark-1.3 Standard · key configured: {state['key_present']} · live enabled: {state['live_enabled']}")
    st.write('One request sends only the note above and extraction schema to api.meta.ai. It may consume credits. Official Standard rates: $1.25 / million input tokens and $4.25 / million output tokens; output capped at 4,096 tokens. No automatic retries.')
    consent=st.checkbox('I authorize one request for this synthetic note and its API usage',key='meta_stock_consent')
    disabled=not(consent and all(state.values())) or st.session_state.get('meta_stock_attempted',False)
    if st.button('Extract synthetic counted stock with Meta',disabled=disabled):
        st.session_state.meta_stock_attempted=True
        st.session_state.pop('meta_stock_candidate',None)
        st.session_state.pop('meta_confirmed_stock',None)
        st.session_state.pop('meta_stock_error',None)
        try:st.session_state.meta_stock_candidate=extract_demo_stock(authorized=True)
        except Exception as exc:st.session_state.meta_stock_error=str(exc)
        st.rerun()
    if st.session_state.get('meta_stock_error'):st.error(st.session_state.meta_stock_error)
    if not all(state.values()):
        st.warning('Live verification blocked: privately configure MODEL_API_KEY and META_LIVE_ENABLED=true in the app launch environment after confirming account access/credits. Never paste the key into chat or GitHub. No new request can be sent while this setup is blocked.')
    record=st.session_state.get('meta_stock_candidate')
    if record:
        st.success('Actual Meta response received; still unconfirmed.')
        st.json({'model':record['model'],'request_id':record['request_id'],'source_hash':record['source_hash'],'usage':record['usage'],'candidate':record['candidate']})
        amounts=candidate_grams(record['candidate'])
        with st.form('confirm_meta_stock'):
            corrected={name:st.number_input(f'Review {name} (g)',min_value=0.0,max_value=1000000.0,
                        value=float(amount) if amount is not None else None,key='meta_review_'+name) for name,amount in amounts.items()}
            reviewed=st.checkbox('I checked every amount against its source quote; use this counted stock for the demo')
            if st.form_submit_button('Confirm stock for Prep Planner'):
                try:
                    audit=confirm_stock(record,corrected,confirmed=reviewed)
                    st.session_state.meta_confirmed_stock=audit
                    for name,value in audit['stock'].items():st.session_state['stock_'+name]=float(value['quantity'])
                    st.success('Confirmed for this session. Open Prep Planner, review its stock form and calculate. No operational database was changed.')
                except ValueError as exc:st.error(str(exc))
    if st.session_state.get('meta_stock_attempted'):
        if st.button('Prepare another attempt (does not call Meta)'):
            for key in list(st.session_state):
                if key.startswith('meta_review_') or key in {'meta_stock_attempted','meta_stock_candidate','meta_confirmed_stock','meta_stock_consent','meta_stock_error'}:
                    del st.session_state[key]
            st.rerun()
    st.caption('Candidate, correction audit and confirmation last only for this browser session. A successful response ID is evidence of a request, not proof the extracted quantities are correct.')
