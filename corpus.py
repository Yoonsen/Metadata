
from collections import Counter
import streamlit as st
#import spacy_streamlit

import pandas as pd
from PIL import Image
import urllib


import dhlab as dh
import dhlab.api.dhlab_api as api
from dhlab.text.nbtokenizer import tokenize
# for excelnedlastning
from io import BytesIO

st.set_page_config(layout="wide")


@st.cache(suppress_st_warning=True, show_spinner=False)
def to_excel(df):
    """Make an excel object out of a dataframe as an IO-object"""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    worksheet = writer.sheets['Sheet1']
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def v(x):
    if x != "":
        res = x
    else:
        res = None
    return res

st.header("Konstruer et korpus" )
st.write("Ler mer om [Nasjonalbibliotekets DH-lab](https://nb.no/dhlab)")
df_defined = False
with st.form(key='my_form'):
    st.subheader('Type tekst og år')
    col1, col2= st.columns(2)
    
    with col1:
        doctype = st.selectbox("Type dokument", ["digibok", "digavis", "digitidsskrift", "digimanus"])
        
    with col2:
        years = st.slider(
        'Årsspenn',
        1810, 2020, (1950, 2000))

   
    
    st.subheader("Forfatter og tittel")
    cola, colb = st.columns(2)
    with cola:
            author = st.text_input("Forfatter", "")

    with colb:
            title = st.text_input("Tittel (også avisnavn)", "")

    st.subheader("Meta- og innholdsdata")
    
    cold, cole, colf, colg = st.columns(4)
    with cold:        
        fulltext = st.text_input("Ord i teksten", "")
    with cole:
        ddk = st.text_input("Dewey desimaltall", "", help="Det matches på starten av desimalkoden. For nøyaktig match, avslutt nummeret med utropstegn !")
        if ddk != "" and not ddk.endswith("!"):
            ddk = f"{ddk}*"
        if ddk.endswith("!"):
            ddk = ddk[:-1]
    with colf:
        subject = st.text_input("Emneord","")
    with colg:
        lang = st.selectbox("Språk", ["nob", "dan", "swe", "sme", "eng", "fra", "spa", "ger"])
    colx, coly = st.columns(2)
    with colx:
        limit = st.number_input("Antall dokument", min_value=1, max_value = 200, value=10)
    with coly:
        filnavn = st.text_input("Filnavn for nedlasting", "korpus.xlsx")
        
    if doctype in ['digimanus']:
        df = dh.Corpus(doctype=v(doctype), limit=limit)
        columns = [['urn','title']]
    elif doctype in ['digavis']:
        df = dh.Corpus(doctype=v(doctype), from_year = years[0], to_year = years[1], title=v(title), limit=limit)
        columns = [['urn','title', 'year', 'timestamp', 'city']]
    elif doctype in ['digitidsskrift']:
        df = dh.Corpus(doctype=v(doctype), author=v(author), from_year = years[0], to_year = years[1], title=v(title), subject=v(subject), ddk= v(ddk), lang=lang, limit=limit)
        columns = [['dhlabid', 'urn', 'title','city','timestamp','year', 'publisher', 'ddc', 'langs']]
    else:
        df = dh.Corpus(doctype=v(doctype), author=v(author), from_year = years[0], to_year = years[1], title=v(title), subject=v(subject), ddk= v(ddk), lang=lang, limit=limit)
        columns = [['dhlabid', 'urn', 'authors', 'title','city','timestamp','year', 'publisher', 'ddc','subjects', 'langs']]

    

    submit_button = st.form_submit_button(label = "Trykk her når korpusdefinisjonen er klar")
    
    if submit_button:
      
        st.dataframe(df.corpus[columns])
        df_defined = True
        
if df_defined:
    if st.download_button('Last ned data i excelformat', to_excel(df.corpus), filnavn, help = "Åpnes i Excel eller tilsvarende"):
        True