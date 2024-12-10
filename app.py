import streamlit as st
from st_cytoscape import cytoscape
from rdflib import Graph, Namespace, RDF

### Some useful variables
ns = Namespace("https://id.kb.se/vocab/")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

### Stylesheet
stylesheet = [
    {
        "selector": "node",
        "style": {
            "content": "data(label)",
            "font-size": "10px",
            "text-valign": "center",
            "text-halign": "center",
            "background-color": "pink",
            "color": "black",
            "overlay-padding": "10px",
            "text-wrap": "wrap",
            "text-max-width": 60,
        },
    },
    {
        "selector": "edge",
        "style": {
            "curve-style": "haystack",
            "haystack-radius": "0.1",
            "opacity": "0.4",
            "line-color": "#bbb",
            "overlay-padding": "1px",
        },
    },
]


data_sources = {"Befintlig uppsättning typer": "https://raw.githubusercontent.com/libris/definitions/refs/heads/develop/source/vocab/things.ttl",
                "Typupsättning under arbete": "https://raw.githubusercontent.com/libris/definitions/refs/heads/feature/typenormalization/source/vocab/things.ttl"}


### Streamlit app
st.set_page_config(layout="wide")

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

with st.form("my_form"):
    with st.sidebar:
        st.write(
            "Designa din visualisering..."
        )
        source = st.selectbox(
            "Välj en datakälla!",
            ("Befintlig uppsättning typer", "Typupsättning under arbete"),
        )

        cy_style = st.selectbox(
            "Väl en visualiseringsstil!",
            ("klay", "cose", "circle","grid","concentric","breadthfirst"),
        )

        
        # Every form must have a submit button.
        submitted = st.form_submit_button("Visualisera!")

        if submitted:
            st.session_state.submitted = True
            st.session_state.cy_style = cy_style
            st.session_state.source = source

if st.session_state.submitted:
    st.write(f"Vald datakälla: {data_sources[source]}")
    st.write(f"Vald visualiseringsstil: {cy_style}")


    ### App functionality
    elements = [{"data": {"id": "work", "label": "Work"}}]
    g = Graph()
    g.parse(data_sources[source],format="turtle")

    # Query for subjects with predicate rdf:subClassOf and object ns.Work
    subjects = list(g.subjects(predicate=rdfs.subClassOf, object=ns.Work))
    message = f'Den valda datakällan innehåller {len(subjects)} direkta underklasser till Work.'

    for subject in subjects:
        # If the labels are more than one (eg @sv and @en)
        # you can either return one ("any") or get a uniqueness error
        label = g.value(subject, rdfs.label, any=True)
        elements.extend(
            [
                {"data": {"id": subject, "label": label}},
                {"data": {"source": "work", "target": subject}},
            ]
        )
        child_subjects = list(g.subjects(predicate=rdfs.subClassOf, object=subject))
        for child_subject in child_subjects:
            child_label = g.value(child_subject, rdfs.label, any=True)
            elements.extend(
                [
                    {"data": {"id": child_subject, 
                                "label": child_label if child_label else f"[{child_subject.lstrip("https://id.kb.se/vocab/")}]"}},
                    {"data": {"source": subject, "target": child_subject}}
                ]
                )

    graph = cytoscape(elements, stylesheet, width="100%", height="600px", layout={"name": cy_style})

