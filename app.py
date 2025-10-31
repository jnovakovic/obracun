import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from energy_billing import izvrši_obracun  # Import your own functions


#st.title("Obračun računa za električnu energiju sa solarnom elektranom",center=True)
st.set_page_config(layout="wide")
st.markdown("""
<div style='text-align: center; font-size:30px; font-family: Arial; font-weight: bold; color: #333;'>
Obračun troška električne energije za kupca sa solarnom elektranom
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True) 

col1, col2 = st.columns([1, 1])
with col1:
    # User input for P_inst
    P_inst = st.number_input('Instalirana snaga solarne elektrane (kW)', min_value=0.0, max_value=30.0, value=4.5, step=0.1, )
    Godišnja_potrošnja = st.number_input('Godišnja potrošnja el. energije', min_value=1000.0, max_value=100000.0, value=5595.4, step=100.0)
    load_coeff=Godišnja_potrošnja/5595.4  # Default load for Load_PV.csv is 5595.4 kWh

# Run calculations
obracun_energije_month, racuni_month, bilanca_month, godišnji_month = izvrši_obracun(P_inst=P_inst,load_coeff=load_coeff, net_interval='month')
obracun_energije_15min, racuni_15min, bilanca_15min,godišnji_15min = izvrši_obracun(P_inst=P_inst, load_coeff=load_coeff,net_interval='15min')
obracun_energije_noPV, racuni_noPV, bilanca_noPV,godišnji_noPV = izvrši_obracun(P_inst=0,load_coeff=load_coeff )

month_names = ['Siječanj', 'Veljača', 'Ožujak', 'Travanj', 'Svibanj', 'Lipanj',
               'Srpanj', 'Kolovoz', 'Rujan', 'Listopad', 'Studeni', 'Prosinac']
 
bills_month = [racuni_month[month].loc[9, 'Iznos EUR'] for month in month_names]
bills_15min = [racuni_15min[month].loc[9, 'Iznos EUR'] for month in month_names]
bills_noPV = [racuni_noPV[month].loc[9, 'Iznos EUR'] for month in month_names]

total_month = bilanca_month.loc['Year', 'Bill']
total_15min = bilanca_15min.loc['Year', 'Bill']
total_noPV = bilanca_noPV.loc['Year', 'Bill']

# Bar plot

x = np.arange(len(month_names))
bar_width = 0.25

fig, ax = plt.subplots(figsize=(8,4))
ax.bar(x - bar_width, bills_noPV, bar_width, label='Bez solarne elektrane', color='gray')
ax.bar(x, bills_month, bar_width, label='Mjesečno netiranje', color='green')
ax.bar(x+bar_width, bills_15min, bar_width, label='15min netiranje', color='orange')

ax.set_xticks(x)
ax.set_xticklabels(month_names, rotation=30,fontsize=8)
ax.tick_params(axis='y', labelsize=8)
ax.set_ylabel('Iznos računa (EUR)',fontsize=8)
ax.set_title('Mjesečni računi za električnu energiju',fontsize=10)
ax.legend(loc='lower left',fontsize=8)
fig.tight_layout()

mid_x = len(month_names) / 2 - 1
max_bill = max(max(bills_month), max(bills_15min), max(bills_noPV))
ax.text(mid_x, max_bill * 1,
         f'Ukupno godišnje \n'
         f'Mjesečno netiranje: {total_month:.2f} EUR\n'
         f'15min netiranje: {total_15min:.2f} EUR\n'
         f'Bez solarne elektrane: {total_noPV:.2f} EUR',
         fontsize=8, ha='center', va='top', bbox=dict(facecolor='white', alpha=0.8))

with col2 :
    st.pyplot(fig)  # Place your wide invoice table here


def plot_bill_style(df):
    df_bill = df[['Opis', 'Iznos EUR']].copy()
    #df_bill=df_bill[df_bill.index<10]
    df_bill['Iznos EUR'] = df_bill['Iznos EUR'].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "")

    fig, ax = plt.subplots(figsize=(12, 0.03 * len(df_bill)))
    
    ax.axis('off')

    table = ax.table(
        cellText=df_bill.values,
        colLabels=df_bill.columns,
        cellLoc='left',
        loc='top',
        colWidths=[0.5, 0.25],
        edges='open'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1)
    for  i in range (2):
        cell = table[0, i]  # row i, column j
        cell.visible_edges = 'B' # Top, Bottom, Left, Right (any combination)
        cell = table[len(df_bill), i]  # row i, column j
        cell.visible_edges = 'TB' # Top, Bottom, Left, Right (any combination)    

    # Style header
    for j in range(len(df_bill.columns)):
        table[0, j].set_text_props(weight='bold')

    # Style rows: left for description, right for amount
    for i in range(0, len(df_bill)+1):
        table[i, 0].set_text_props(ha='left')
        table[i, 1].set_text_props(ha='right')
        # Optionally bold total row (last row)
        if i == len(df_bill):
            table[i, 1].set_text_props(weight='bold')
            table[i, 0].set_text_props(weight='bold')
    fig.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
     
    #fig.tight_layout()
    return fig

def plot_bill_style2(df):
    df_bill = df[['Opis','Stanje od','Stanje do','Potrošak']].copy()
    df_bill['Potrošak'] = df_bill['Potrošak'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")  
    df_bill['Stanje od'] = df_bill['Stanje od'].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "") 
    df_bill['Stanje do'] = df_bill['Stanje do'].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "")   
    
    df_bill.loc[11, 'Stanje od'] = ''
    df_bill.loc[11, 'Stanje do'] = '' 
    df_bill.loc[11, 'Potrošak'] = ''
   

    #fig, ax = plt.subplots(figsize=(12, 0.7 + 0.55*len(df_bill)))
    fig, ax = plt.subplots(figsize=(12, 0.08 * len(df_bill)))
    
    ax.axis('off')

    table = ax.table(
        cellText=df_bill.values,
        colLabels=df_bill.columns,
        cellLoc='left',
        loc='top',
        colWidths=[0.3, 0.15,0.15,0.15],
        edges='open'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1)
    for  i in range (4):
        cell = table[0, i]  # row i, column j
        cell.visible_edges = 'B' # Top, Bottom, Left, Right (any combination)
        cell = table[len(df_bill), i]  # row i, column j
        cell.visible_edges = 'B' # Top, Bottom, Left, Right (any combination)    

    # Style header
    for j in range(len(df_bill.columns)):
        table[0, j].set_text_props(weight='bold')

    # Style rows: left for description, right for amount
    for i in range(0, len(df_bill)+1):
        table[i, 0].set_text_props(ha='left')
        table[i, 1].set_text_props(ha='center')
        table[i, 2].set_text_props(ha='center')
        table[i, 3].set_text_props(ha='center')
          
    fig.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
     
    #fig.tight_layout()
    return fig

def plot_bill_style3(df):
    df_bill = df[['Opis','Iznos EUR','Količina','Jedinica mjere','Cijena EUR/kWh']].copy() 
    df_bill['Iznos EUR'] = df_bill['Iznos EUR'].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "") 
    df_bill['Količina'] = df_bill['Količina'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "") 
    df_bill['Jedinica mjere'] = df_bill['Jedinica mjere'].apply(lambda x: "" if pd.isnull(x) else x)
    df_bill['Cijena EUR/kWh'] = df_bill['Cijena EUR/kWh'].apply(lambda x: f"{x:,.6f}" if pd.notnull(x) else "")
    df_bill['Cijena EUR/kWh'] = df_bill['Cijena EUR/kWh'].apply(lambda x: "" if pd.isnull(x) else x)

    df_bill.rename(columns={'Cijena EUR/kWh': 'EUR/kWh'}, inplace=True)
    df_bill.rename(columns={'Jedinica mjere': 'Jedinica'}, inplace=True)   
   
    fig, ax = plt.subplots(figsize=(12, 0.01 * len(df_bill)))    
    ax.axis('off')

    table = ax.table(
        cellText=df_bill.values,
        colLabels=df_bill.columns,
        cellLoc='left',
        loc='top',
        colWidths=[0.5, 0.1,0.1,0.05,0.1],
        edges='open'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1)
    for  i in range (5):
        cell = table[0, i]  # row i, column j
        cell.visible_edges = 'B' # Top, Bottom, Left, Right (any combination)
        cell = table[len(df_bill), i]  # row i, column j
        cell.visible_edges = 'B' # Top, Bottom, Left, Right (any combination)    

    # Style header
    for j in range(len(df_bill.columns)):
        table[0, j].set_text_props(weight='bold')

    # Style rows: left for description, right for amount
    for i in range(0, len(df_bill)+1):
        table[i, 0].set_text_props(ha='left')
        table[i, 1].set_text_props(ha='center')
        table[i, 2].set_text_props(ha='center')
        table[i, 3].set_text_props(ha='center')
        table[i, 4].set_text_props(ha='center')
    for i in range(0, len(df_bill)+1):
        if i in ([4,7, 13,14]):
            for j in range(5):
                table[i, j].set_text_props(weight='bold')
                cell = table[i, j]
                cell.visible_edges = 'T' # Top, Bottom, Left, Right (any combination
            for j in [2,3,4]:
                table[i, j].get_text().set_text("")
        elif i in ([17,18]):
            for j in range(2):
                table[i, j].set_text_props(weight='bold')
               
       
          
    fig.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
     
    #fig.tight_layout()
    return fig

fig = plot_bill_style(godišnji_month[godišnji_month.index<10])
fig1 = plot_bill_style2(godišnji_month[(godišnji_month.index > 10) & (godišnji_month.index < 16)])
fig4 = plot_bill_style3(godišnji_month[godišnji_month.index>15])

fig2 = plot_bill_style(godišnji_15min[godišnji_15min.index<10])
fig3 = plot_bill_style2(godišnji_15min[(godišnji_15min.index > 10) & (godišnji_15min.index < 16)])
fig5 = plot_bill_style3(godišnji_15min[godišnji_15min.index>15])

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; font-size:25px; font-family: Arial; font-weight: bold; color: #333;'>
Godišnji sažetak računa
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True) 

st.markdown(f"""
    <div style="
        border: 2px solid black;  /* red border */
        padding: 10px;               /* space inside */
        border-radius: 8px;          /* rounded corners */
        text-align: left;          /* center the text */
        font-family: Arial, sans-serif;
        font-size: 14px;
        background-color: light-gray;
        color: #333;">
            Usporedba godišnjeg troška el. energije: <br>
            <br>
            - za kupce sa solarnom elektranom - korisnike postrojenja za SAMOOPSKRBU, gdje se kod obračuna koristi mjesečno netiranje energije \
            (na kraju mjeseca može postojati višak ili manjak energije u pojedinoj tarifi tj. ili preuzeta ili energija predana u mrežu će biti jednaka nuli). <br>
            <br>
            - za kupce sa solarnom elektranom - kupce s VLASTITOM PROIZVODNJOM te korisnike postrojenja za SAMOOPSKRBU od 1.1.2026., gdje se kod obračuna koristi netiranje energije u 15 min intervalima \
             (na kraju mjeseca može postojati višak i manjak energije u pojedinoj tarifi tj. i preuzeta i energija predana u mrežu su veće od nule). <br>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True) 

col1, col2 = st.columns([1, 1])
with col1:  
    st.markdown("""
                <div style='text-align: center; font-size:15; font-family: Arial;font-weight: bold; color: #333;'>
                Samoopskrba - mjesečno netiranje
                </div>
                """, unsafe_allow_html=True)  
    st.pyplot(fig) 
    st.pyplot(fig1)
    st.pyplot(fig4)    


with col2:  
    st.markdown("""
                <div style='text-align: center; font-size:15; font-family: Arial;font-weight: bold; color: #333;'>
                Vlastita proizvodnja - 15 min netiranje
                </div>
                """, unsafe_allow_html=True)  
    st.pyplot(fig2)
    st.pyplot(fig3)
    st.pyplot(fig5)      


st.markdown(f"""
<div style="
    border: 2px solid #FFCCCC;  /* green border */
    padding: 10px;               /* space inside */
    border-radius: 8px;          /* rounded corners */
    text-align: center;          /* center the text */
    font-family: Arial, sans-serif;
    font-size: 14px;
    background-color: #FFF5F5;
    color: #333;">
     *Razlika između potroška ({godišnji_month.loc[12,'Potrošak']:.0f}) i stanja mjerila ({godišnji_month.loc[12,'Stanje do']:.2f}) nastaje zbog zaokruživanja kWh na cijeli broj kod kreiranja mjesečnog računa
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True) 

col1, col2 = st.columns([1, 1])
with col1: 
    st.markdown(f"""
    <div style="
        border: 2px solid #4CAF50;  
        padding: 10px;              
        border-radius: 8px;         
        text-align: left;         
        font-family: Arial, sans-serif;
        font-size: 14px;
        background-color: #f9f9f9;
        color: #333;">
            SAMOOPSKRBA -  MJESEČNO  NETIRANJE energije: <br> 
            dio el. en. predane u mrežu koji preuzima opskrbljivač odgovara zbroju mjesečnih viškova energije u odgovarajućoj tarifi, <br>
            te se obračunava se po cijeni od 80% cijene opskrbe po kWH ({godišnji_month.loc[32,'Količina']:.0f} kWh za VT).<br>
            Ostatak ({(godišnji_month.loc[14,'Potrošak']-godišnji_month.loc[32,'Količina']):.0f} od ukupno {godišnji_month.loc[14,'Potrošak']:.0f} kWh u VT)\
            pri obračunu se oduzima od el.en. preuzete iz mreže\
            ({godišnji_month.loc[12,'Potrošak']:.0f} - {(godišnji_month.loc[14,'Potrošak']-godišnji_month.loc[32,'Količina']):.0f} = {godišnji_month.loc[16,'Količina']:.0f} kWh u VT)  
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="
        border: 2px solid #FFA500;  /* red border */
        padding: 10px;               /* space inside */
        border-radius: 8px;          /* rounded corners */
        text-align: left;          /* center the text */
        font-family: Arial, sans-serif;
        font-size: 14px;
        background-color: #FFF3E6;
        color: #333;">
                VLASTITA PROIZVODNJA I SAMOOPSKRBA OD 1.1.2026. <br>
                Bez netiranja energije na mjesečnoj razini, el. en. predanu u mrežu  ({godišnji_15min.loc[32,'Količina']:.0f} kWh za VT, {godišnji_15min.loc[33,'Količina']:.0f} kWh za NT) preuzima opskrbljivač po cijeni:<br>        
                - Ci = 0,9 * PKCi, ako za obračunsko razdoblje i vrijedi: Epi >= Eii <br>
                - Ci = 0,9 * PKCi * Epi/Eii, ako za obračunsko razdoblje i vrijedi Epi < Eii <br>
                gdje je: <br>
                Epi = ukupna električna energija preuzeta iz mreže na obračunskom mjernom mjestu krajnjeg kupca u obračunskom razdoblju, izražena u kWh  <br>
                Eii = ukupna električna energija isporučena u mrežu na obračunskom mjernom mjestu krajnjeg kupca u obračunskom razdoblju, izražena u kWh  <br>
                PKCi = prosječna jedinična cijena električne energije koju krajnji kupac plaća opskrbljivaču za prodanu električnu energiju (cijena po kWh samo za opskrbu!) \
                      - na računu izračunata kao cijena za neto višak energije ({godišnji_15min.loc[32,'Cijena EUR/kWh']:.6f} EUR/kWh)
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True) 



st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; font-size:25px; font-family: Arial; font-weight: bold; color: #333;'>
Mjesečni računi
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True) 

col1, col2 = st.columns([1, 1])
with col1:
    for month in month_names:
        st.markdown(f"""
            <div style='text-align: center; font-size:20; font-family: Arial; font-weight: bold; color: blue;'>
            {month}
            </div>
            """, unsafe_allow_html=True)
        #st.markdown("<br>", unsafe_allow_html=True) 
        racun=racuni_month[month]
        fig1 = plot_bill_style(racun[racun.index<10])
        fig2 = plot_bill_style2(racun[(racun.index > 10) & (racun.index < 16)])
        fig3 = plot_bill_style3(racun[racun.index>15])
        st.pyplot(fig1)
        st.pyplot(fig2)
        st.pyplot(fig3)

with col2:
    for month in month_names:
        st.markdown(f"""
            <div style='text-align: center; font-size:20; font-family: Arial; font-weight: bold; color: blue;'>
            {month}
            </div>
            """, unsafe_allow_html=True)
        #st.markdown("<br>", unsafe_allow_html=True) 
        racun=racuni_15min[month]
        fig1 = plot_bill_style(racun[racun.index<10])
        fig2 = plot_bill_style2(racun[(racun.index > 10) & (racun.index < 16)])
        fig3 = plot_bill_style3(racun[racun.index>15])
        st.pyplot(fig1)
        st.pyplot(fig2)
        st.pyplot(fig3)
       




