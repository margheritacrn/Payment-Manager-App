import streamlit as st
import numpy as np
import streamlit.components.v1 as components


def predict_service(relative_declines: tuple, verbose=False)-> int:
    assert(len(relative_declines) == 4)
    intial_condition = 4 # P_0 = 4v, asset nav at the beginning of year 1
    relative_declines = np.array(relative_declines)
    decline_factors = np.ones(4) - relative_declines 
    p_coeff = 2/10 # the instalment is the same for each year: 2/10*v
    donation_factor1 = 2.5/100
    donation_factor2 = 5/100
    budget= sum(decline_factors[:2]) # limit value for the sum of the outflows
    donations = np.zeros(3)
    outflows = np.zeros(3)
    portfolio_coeffs = np.zeros(3)
    # initialize with values for year 1
    donations[0] = donation_factor1*intial_condition + donation_factor2*decline_factors.sum() # initialize with donation for year 1
    outflows[0] = donations[0]+p_coeff 
    portfolio_coeffs[0] = decline_factors.sum()
    
    if (outflows[0] >= budget): # if the first outflow is already greater than the budget we won't be able to service
        if(verbose):
            st.write("Your portfolio has exceeded the limit value")
        return -1
    else:
        for i in range(1,3):
            donations[i] = donation_factor1*portfolio_coeffs[-1]+ 0.5*donations[i-1]
            outflows[i] = donations[i]+p_coeff
            portfolio_coeffs[i] = np.round(portfolio_coeffs[i-1] - outflows[i-1],2)
            if(sum(outflows) >= budget):
                if(verbose):
                    st.write("Your portfolio has exceeded the limit value")
                return -1
            else:
                continue
        if(verbose):
            st.write("\nYou will be able to service your payments and commitments!")
        return 0


# set initial states for all the widgets and buttons
state = st.session_state
if 'STOCKS_DEC' not in state:
    state.STOCKS_DEC = 0.33
if 'BONDS_DEC' not in state:
    state.BONDS_DEC = 0.2
if 'FLAT1_DEC' not in state:
    state.FLAT1_DEC = 0.1
if 'FLAT2_DEC' not in state:
    state.FLAT2_DEC = 0.1
if 'N_SAMPLES' not in state:
    state.N_SAMPLES = 1000
if 'clicked_ws' not in state:
    state.clicked_ws = False
if 'clicked_multiple_ws' not in state:
    state.clicked_multiple_ws = False
    

def set_state_value_ws():
    state.STOCKS_DEC = state['stocks_dec']
    st.session_state[2] = True
    state.BONDS_DEC = state['bonds_dec']
    state.FLAT1_DEC = state['flat1_dec']
    state.FLAT2_DEC = state['flat2_dec']


def set_state_value_samp():
    state.N_SAMPLES = state['n_samples']


def click(button):
    if(button == 'ws'):
        state.clicked_ws = True
        state.clicked_multiple_ws = False
    else:
        state.clicked_ws = False
        state.clicked_multiple_ws = True
     

# Set title and intialize containers
st.title('Task solver') 
container1 = st.container()
container2 = st.container()
container3 = st.container()

# fill containers
with container1:
    html_string = '''
        <script language="javascript">
          document.querySelector("h2").style.color = "red";
        </script>
        '''
    components.html(html_string, width=10, height=10)
    portfolio = st.expander('Portfolio')
    payments_and_commitments = st.expander('Payments and commitments')
    predict_s = st.expander('Predict service')
    # PORTFOLIO
    with portfolio: # show portfolio structure and details of investments
        with st.popover("Stocks (25%) and bonds (25%)"):
            st.markdown("- sealable, don't appreciate/depreciate")
        with st.popover("flat in Berlin (25%) and in Potsdam (25%)"):
            st.markdown("- no rental income")
            st.markdown("- purchased in January, bank loan of 30% of the price")
    # OUTFLOWS
    with payments_and_commitments: # show details on payments and commitments
        with st.popover("Yearly instalments to the bank"):
            st.markdown("- each instalment is 10% of initial value of the flats")
            st.markdown("- no interest charged")
        with st.popover("Yearly donations"):
            st.markdown("- 2.5% of the  beginning-of-year portfolio value")
            st.markdown("- at least half of last year's donation")
    # PREDICT        
    if 'show_inputs' not in st.session_state:
        st.session_state.show_inputs = False
    
  
    st.write("Predict whether you will be able to service the debt and commitments in a worst case scenario")
    col1, col2 = st.columns(2)
    with col1:
        ws = st.button('Choose a worst case scenario', key='ws_button', on_click=click, args=['ws'])
    with col2:
        sample_ws = st.button('Sample worst case scenarios', on_click=click, args=['multiple_ws'])
    # single worst case scenario
    if state.clicked_ws:
            st.session_state.show_inputs = True
            if st.session_state.show_inputs:
                st.write('Provide relative declines for your assets')
                stocks_dec = st.slider("Stocks decline rate", min_value=0.0, max_value=1.0, value=state.STOCKS_DEC, step=0.01, key='stocks_dec',
                                    on_change=set_state_value_ws)
                bonds_dec = st.slider("Bonds decline rate", min_value=0.0, max_value=1.0, value=state.BONDS_DEC, step=0.01, key='bonds_dec',
                                    on_change=set_state_value_ws)
                flat1_dec = st.slider('Flat in Berlin decline rate', min_value=0.0, max_value=1.0, value=state.FLAT1_DEC, step=0.01, key='flat1_dec',
                                    on_change=set_state_value_ws)
                flat2_dec = st.slider('Flat in Potsdam decline rate', min_value=0.0, max_value=1.0, value=state.FLAT2_DEC, step=0.01, key='flat2_dec',
                                    on_change=set_state_value_ws)
                rel_decs = tuple([stocks_dec, bonds_dec, flat1_dec, flat2_dec])
                submit_decs = st.button('Run')
                if submit_decs:
                    _ = predict_service(rel_decs, verbose=True)
                    state.clicked_ws = False
                
    # sample n worst case scenarios
    if state.clicked_multiple_ws:
        n_samples = st.number_input(label='Number of samples', min_value=0, max_value=2000, value=state.N_SAMPLES, key='n_samples',
                                    on_change=set_state_value_samp)
        if st.button('Run'):
                random_relative_declines = [tuple(round(np.random.uniform(0,1),2) for _ in range(4)) for _ in range(n_samples)] 
                service_outcomes = {}
                for relative_declines in random_relative_declines:
                    service_outcome = predict_service(relative_declines)
                    service_outcomes[relative_declines] = service_outcome
                num_positive_outcomes = len(list(filter(lambda o: o == 0, service_outcomes.values())))
                st.write(f"Number of times it was possible to service debt and commitments: {num_positive_outcomes}/{n_samples}")

            
    