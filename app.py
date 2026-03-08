import streamlit as st
import requests
import pandas as pd
import time
import plotly.express as px

PINECONE_API_KEY =  st.secrets['PINECONE_API']
connection_string1 = st.secrets["MONGODB_CONNECTION_STRING"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# MFAPI helpers (replaces mftool)
_MFAPI = "https://api.mfapi.in/mf"

def get_available_schemes(amc_name):
    r = requests.get(f"{_MFAPI}/search", params={"q": amc_name}, timeout=10)
    r.raise_for_status()
    return {str(item["schemeCode"]): item["schemeName"] for item in r.json()}

def get_scheme_quote(scheme_code):
    r = requests.get(f"{_MFAPI}/{scheme_code}/latest", timeout=10)
    r.raise_for_status()
    resp = r.json()
    meta = resp.get("meta", {})
    data = resp.get("data", [{}])
    return {"scheme_code": str(scheme_code), "scheme_name": meta.get("scheme_name", ""),
            "nav": data[0].get("nav", "") if data else "", **meta}

def get_scheme_details(scheme_code):
    r = requests.get(f"{_MFAPI}/{scheme_code}", timeout=10)
    r.raise_for_status()
    meta = r.json().get("meta", {})
    return {"scheme_code": str(scheme_code), "scheme_name": meta.get("scheme_name", ""),
            "fund_house": meta.get("fund_house", ""), "scheme_type": meta.get("scheme_type", ""),
            "scheme_category": meta.get("scheme_category", ""), **meta}

def get_scheme_historical_nav(scheme_code):
    r = requests.get(f"{_MFAPI}/{scheme_code}", timeout=10)
    r.raise_for_status()
    return r.json()
# Custom CSS to style the app with a modern blue theme

# Create tabs
tabs = st.tabs(["Project Description" , "Mutual Fund Tools","Finnace Chat Bot"])

with tabs[1]:
    # Custom CSS to style the app with a modern black theme
    st.markdown("""
        <style>
        /* Background color for the app */
        .stApp {
            background-color: #121212;
            color: #ffffff;
        }

        /* Sidebar styling */
        .sidebar .sidebar-content {
            background-color: #1e1e1e;
            color: white;
        }

        /* Title styling */
        .st-title {
            color: #ffffff;
            font-size: 40px;
            font-weight: bold;
        }

        /* Progress bar color */
        .stProgress > div > div {
            background-color: #ff4081;
        }

        /* DataFrame container styling */
        .stDataFrame {
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);
        }

        /* Input text and button styling */
        .stTextInput > div > div input {
            border: 2px solid #ff4081;
            border-radius: 8px;
            padding: 10px;
            background-color: #1e1e1e;
            color: #ffffff;
        }

        .stButton > button {
            background-color: #ff4081;
            color: white;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            transition: background-color 0.3s;
        }

        .stButton > button:hover {
            background-color: #d5006d;
        }

        /* Style for the radio buttons */
        .stRadio > label > div > div {
            color: #ff4081;
        }

        /* Styling for json and error messages */
        .stJson {
            background-color: #e8f0fe;
            border-radius: 8px;
            padding: 10px;
            color: #000000;
        }

        .stError {
            color: #ff4081;
        }

        /* Chart styling */
        .plotly {
            background-color: #121212;
        }
        </style>
    """, unsafe_allow_html=True)

    # Title
    st.markdown("<div class='st-title'>Mutual Fund Tools App</div>", unsafe_allow_html=True)

    # Sidebar with selectbox to choose an action
    st.sidebar.title("Menu")
    menu_option = st.sidebar.selectbox("Choose an Action", [
        "Get Available Schemes under AMC",
        "Get Scheme Quote (Current NAV)",
        "Get Scheme Details",
        "Get Historical NAV Data"
    ])

    # Initialize empty containers for updating dynamically
    data_placeholder = st.empty()
    progress_placeholder = st.empty()

    # 1. Get Available Schemes under AMC
    if menu_option == "Get Available Schemes under AMC":
        amc_name = st.text_input("Enter AMC Name (e.g., 'ICICI')", value="HDFC")
        
        # Use radio button to allow user to select a filter for schemes
        filter_choice = st.radio("Filter Options", ("Show All Schemes", "Show only Equity Schemes", "Show only Debt Schemes"))
        
        # Nested filter choice based on user's selection
        additional_filter = None
        if filter_choice != "Show All Schemes":
            additional_filter = st.selectbox("Select additional filter", ["Filter 1", "Filter 2"])

        if st.button("Get Schemes"):
            try:
                progress = progress_placeholder.progress(0)  # Show progress bar
                schemes = get_available_schemes(amc_name)
                if schemes:
                    # Filter based on user selection
                    if filter_choice == "Show only Equity Schemes":
                        schemes = {k: v for k, v in schemes.items() if "Equity" in v}
                    elif filter_choice == "Show only Debt Schemes":
                        schemes = {k: v for k, v in schemes.items() if "Debt" in v}
                    
                    # Convert the schemes to DataFrame
                    df = pd.DataFrame(list(schemes.items()), columns=["Scheme Code", "Scheme Name"])
                    
                    # Update the progress bar
                    progress.progress(50)
                    time.sleep(1)  # Simulate a delay

                    # Display the DataFrame using st.dataframe with advanced features
                    data_placeholder.dataframe(df.style.set_properties(**{
                        'background-color': '#1e1e1e',
                        'color': '#ff4081',
                        'border': '1px solid #ff4081',
                        'border-radius': '10px',
                        'font-family': 'Arial',
                        'font-size': '14px'
                    }), use_container_width=True)

                    # Full progress completion
                    progress.progress(100)
                    progress_placeholder.empty()  # Clear the progress bar
                else:
                    st.error("No schemes found for this AMC.")
            except Exception as e:
                st.error(f"Error: {e}")
                progress_placeholder.empty()  # Clear the progress bar

    # 2. Get Scheme Quote (Current NAV)
    elif menu_option == "Get Scheme Quote (Current NAV)":
        scheme_code = st.text_input("Enter Scheme Code", value="151729")
        
        # Radio button for different data view filters
        view_type = st.radio("View Options", ("Basic Info", "Full Info"))

        if st.button("Get Scheme Quote"):
            try:
                quote = get_scheme_quote(scheme_code)
                if quote:
                    st.write(f"Quote for Scheme {scheme_code}:")
                    if view_type == "Basic Info":
                        st.json({
                            "scheme_code": quote["scheme_code"],
                            "scheme_name": quote["scheme_name"],
                            "nav": quote["nav"]
                        })
                    else:
                        st.json(quote)  # Show full information
                else:
                    st.error("No quote found for this scheme code.")
            except Exception as e:
                st.error(f"Error: {e}")

    # 3. Get Scheme Details
    elif menu_option == "Get Scheme Details":
        scheme_code = st.text_input("Enter Scheme Code for Details", value="151729")
        
        # Radio button for detail level
        detail_level = st.radio("Detail Level", ("Basic", "Extended"))
        
        if st.button("Get Scheme Details"):
            try:
                scheme_details = get_scheme_details(scheme_code)
                if scheme_details:
                    st.write(f"Details for Scheme {scheme_code}:")
                    if detail_level == "Basic":
                        st.json({
                            "scheme_code": scheme_details["scheme_code"],
                            "scheme_name": scheme_details["scheme_name"],
                            "fund_house": scheme_details["fund_house"],
                        })
                    else:
                        st.json(scheme_details)  # Show full details
                else:
                    st.error("No details found for this scheme code.")
            except Exception as e:
                st.error(f"Error: {e}")

    # 4. Get Historical NAV Data
     # Get Historical NAV Data along with Scheme Details
    # Get Historical NAV Data along with Scheme Details
    elif menu_option == "Get Historical NAV Data":
        scheme_code = st.text_input("Enter Scheme Code for Historical NAV", value="151729")
        
        # Radio button to choose the output format
        output_format = st.radio("Output Format", ("Table", "JSON"))

        if st.button("Get Historical NAV"):  # Only execute the following after the button is pressed
            try:
                # Fetch scheme details first
                scheme_details = get_scheme_details(scheme_code)
                
                if scheme_details:
                    st.write(f"Details for Scheme Code {scheme_code}:")
                    # Display basic scheme information above the graph
                    st.json({
                        "Scheme Name": scheme_details.get("scheme_name", "N/A"),
                        "Fund House": scheme_details.get("fund_house", "N/A"),
                        "Scheme Type": scheme_details.get("scheme_type", "N/A"),
                        "Scheme Category": scheme_details.get("scheme_category", "N/A")
                    })
                else:
                    st.error("No scheme details found for this scheme code.")
                
                # Fetch historical NAV data
                historical_nav = get_scheme_historical_nav(scheme_code)
                
                # Extracting date and nav data into a DataFrame
                data = historical_nav['data']
                historical_nav_df = pd.DataFrame(data)

                # Convert 'date' to datetime format and 'nav' to float
                historical_nav_df['date'] = pd.to_datetime(historical_nav_df['date'], format='%d-%m-%Y')
                historical_nav_df['nav'] = historical_nav_df['nav'].astype(float)

                # Check if the DataFrame is not empty
                if not historical_nav_df.empty:
                    # Display DataFrame only after button is clicked
                    data_placeholder.dataframe(historical_nav_df.style.set_properties(**{
                        'background-color': '#1e1e1e',
                        'color': '#ff4081',
                        'border': '1px solid #ff4081',
                        'border-radius': '10px',
                        'font-family': 'Arial',
                        'font-size': '14px'
                    }), use_container_width=True)

                    # Plotting the line chart
                    fig = px.line(historical_nav_df, x='date', y='nav', 
                                title="NAV Over Time", 
                                labels={"date": "Date", "nav": "NAV"},
                                hover_data={"date": "|%d-%m-%Y", "nav": ":.2f"})
                    
                    # Customize the layout
                    fig.update_traces(line_color="#ff4081")
                    fig.update_layout(hovermode="x unified", xaxis_title="Date", yaxis_title="NAV",
                                    plot_bgcolor='#121212', paper_bgcolor='#121212',
                                    font=dict(color="#ffffff"))

                    # Show the plot
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                else:
                    st.error("No historical NAV data found.")
            except Exception as e:
                st.error(f"Error: {e}")


with tabs[0]:
    # Project description content
    st.markdown("""
    # Project Description
    This application provides various tools for exploring and analyzing mutual fund data using the Mftool library. 
    It includes features such as:

    - Viewing available schemes under a specific Asset Management Company (AMC).
    - Obtaining the current Net Asset Value (NAV) quote for a scheme.
    - Viewing detailed information about a particular mutual fund scheme.
    - Displaying historical NAV data with visualization for better analysis.

    ## Features:
    - Interactive user interface with a modern black theme.
    - Filtering options to view equity or debt schemes.
    - Visualization using Plotly for historical NAV trends.

    This tool is particularly useful for investors looking to track and analyze mutual fund performance efficiently.
    """)

with tabs[2]:
    import os
    import streamlit as st
    import warnings
    from dotenv import load_dotenv
    from pymongo import MongoClient, ASCENDING
    from datetime import datetime
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    from langchain_community.chat_message_histories import MongoDBChatMessageHistory
    from langchain_core.messages import AIMessage, HumanMessage
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_pinecone import PineconeVectorStore
    from langchain_groq import ChatGroq
    from pinecone import Pinecone, ServerlessSpec
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma
    from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
    from groq import Groq
    import joblib
    import nest_asyncio  # noqa: E402
    nest_asyncio.apply()
    


    chat_message_history = MongoDBChatMessageHistory(
            session_id="test_session",
            connection_string=connection_string1,
            database_name="amiteshpatrabtech2021",
            collection_name="chat_histories",
        )

    # MongoDB connection setup
    def get_mongo_client():
        connection_string = connection_string1

        client = MongoClient(connection_string)
        return client

    # Create TTL index to expire chat history after 7 days
    def create_ttl_index():
        client = get_mongo_client()
        db = client['amiteshpatrabtech2021']
        collection = db['chat_histories']

        # Create the TTL index on 'createdAt' field
        collection.create_index([("createdAt", ASCENDING)], expireAfterSeconds=604800)

    # Function to display chat history from MongoDB
    def see_chat_history():
        create_ttl_index()  # Ensure the TTL index is created

        chat_message_history = MongoDBChatMessageHistory(
            session_id="test_session",
            connection_string= connection_string1,
            database_name="amiteshpatrabtech2021",
            collection_name="chat_histories",
        )

        if not chat_message_history.messages:
            return []

        history = []
        for message in chat_message_history.messages:
            if isinstance(message, AIMessage):
                history.append(("AI", message.content))
            elif isinstance(message, HumanMessage):
                history.append(("human", message.content))
        return history

    def save_chat_message(message_content, role="human"):
        client = get_mongo_client()
        db = client['amiteshpatrabtech2021']
        collection = db['chat_histories']

        message_data = {
            "content": message_content,
            "role": role,
            "createdAt": datetime.utcnow()
        }
        collection.insert_one(message_data)

    # Function to delete all chat history
    def delete_chat_history():
        client = get_mongo_client()
        db = client['amiteshpatrabtech2021']
        collection = db['chat_histories']

        result = collection.delete_many({})
        st.sidebar.write(f"Deleted {result.deleted_count} messages from the chat history.")

    # Sidebar for deleting chat history
    st.sidebar.title("Manage Chat History")
    if st.sidebar.button("Delete Chat History"):
        delete_chat_history()
        st.sidebar.success("Chat history has been deleted.")

    # Set up the Pinecone vector store and embeddings
    
    
    # Initialize Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index_name = "mf-rag"

    # Check if index exists, create if it doesn't
    existing_indexes = [index.name for index in pc.list_indexes()]

    if index_name not in existing_indexes:
        print(f"Creating index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=384,  # all-MiniLM-L6-v2 uses 384 dimensions
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"  # Change to your preferred region
            )
        )
        # Wait for index to be ready
        import time
        time.sleep(10)
        print(f"Index {index_name} created successfully")
    else:
        print(f"Using existing index: {index_name}")

    # Now connect to the index
    index = pc.Index(index_name)

    # Continue with embeddings and vector store
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)

    # Define retriever with similarity score threshold
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 1, "score_threshold": 0.5},
    )

    # Define custom prompt template
    prompt_template = """
    Use the following pieces of information to answer the user's question.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Context: {context}
    Question: {input}

    Only return the helpful answer below and nothing else.
    Helpful answer:
    """
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "input"])

    # Set up ChatGroq model
    chat_model = ChatGroq(temperature=0.2, model_name="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)


    def _format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Pure LCEL chain: retrieve → format → prompt → LLM → parse
    qa = (
        {"context": retriever | _format_docs, "input": RunnablePassthrough()}
        | PROMPT
        | chat_model
        | StrOutputParser()
    )

    def get_response(user_input):
        return qa.invoke(user_input)

    # Streamlit UI setup
    st.title("AIBF Chatbot")

    

    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Save user message to MongoDB chat history
        save_chat_message(user_input, "human")

        # Get RAG-based response using the updated QA chain
        response = get_response(user_input)

        
        save_chat_message(response, "ai")

    # Chat interface
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello I am your Mutual fund advisor . How can I help you?")
        ]

    if "vector_store" not in st.session_state:
        st.session_state.vector_store = vector_store

    if user_input:
        response = get_response(user_input)
        st.session_state.chat_history.append(HumanMessage(content=user_input))
        st.session_state.chat_history.append(AIMessage(content=response))

    # conversation
    for index, message in enumerate(st.session_state.chat_history):
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                chat_message_history.add_ai_message(message.content)
                st.write(message.content)
                
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                chat_message_history.add_user_message(message.content)
                st.write(message.content)
    with st.sidebar:
        st.header("AIBF Chatbot")
        st.subheader("By Nishkka")
        
