import streamlit as st
import psycopg2
from dotenv import load_dotenv
import os
import pandas as pd
from db_utilities import get_products, price_diff, reserve_product, kg_saved, purchase_product, purchase_total, purchase_kg_total
from streamlit_extras.bottom_container import bottom
from streamlit_extras.stylable_container import stylable_container


#background color
st.markdown(
    """
    <style>
    .stApp {
        background-color: #256670;
    }
    </style>
    """,
    unsafe_allow_html=True
)
#bottom bar color

css_style = """
    background-color: #1E425E;
    border-radius: 5px;
    padding: 10px;
    """




# Load environment variables
load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")


# Will display the full dataframe in a frozen box
# to be called whenever something is updated
def display_df(conn):
    df = get_products(conn)
    return st.dataframe(df)
    


# -- MAIN CODE BEGINS HERE -- db connection
conn = psycopg2.connect(user=USER, password=PASSWORD, host=HOST, port=PORT, dbname=DBNAME)

st.title("Salvage Style Backend Prototype")

df = get_products(conn)



#dropdown list of products
# when you select a product to add to cart, it will display your savings
product_names = df["name"].tolist()
selected_name = st.selectbox("Select a product to add to the cart", product_names)
selected_product = df[df["name"] == selected_name].iloc[0]
selected_id = int(selected_product["id"])




#add to cart button - will update the 
with st.form("add_to_cart_form"):
    submitted = st.form_submit_button("Add to cart")
    if submitted:
        result = reserve_product(conn, selected_id)
        if result == "reserved":
            st.success(f'"{selected_name}" added to cart and reserved!')
            df = get_products(conn)
        else:
            st.warning(f'"{selected_name}" is already reserved.')

#display money saved and textile rescued
diff = price_diff(conn, selected_id)
st.write("By purchasing this item you will")
st.write(f"Save: ${diff:.2f}")
weight_kg = kg_saved(conn, selected_id)
st.write(f"Rescue: {weight_kg:,.3f} kg of textile")

with st.form("purchase_in_cart"):
    submitted = st.form_submit_button("Checkout")
    if submitted:
        purchase_product(conn)
        totalM = purchase_total(conn)
        totalKG = purchase_kg_total(conn)
        st.write(f"Checkout Total: ${totalM:.2f}")
        st.write(f"Total amount of textile saved: {totalKG:,.3f}")


    
        

with st.form("reset_table_form"):
    submitted = st.form_submit_button("Reset Demo")
    if submitted:
        cursor = conn.cursor()
        cursor.execute('UPDATE "Products" SET status = %s', ('Available',))
        conn.commit()
        cursor.close()
        #refresh the dataframe, redisplay in the sidebar
        df = get_products(conn)
        
# bottom bar to constantly display the dataframe
with bottom():
    with stylable_container(key="bottom_container_style", css_styles=css_style):
        st.title("📊 Database Snapshot")
        st.dataframe(df, use_container_width=True)
    


conn.close()