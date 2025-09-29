import streamlit as st
import psycopg2
from dotenv import load_dotenv
import os
import pandas as pd



#get the data frame
def get_products(conn):

    df = pd.read_sql('SELECT * FROM "Products" WHERE status != %s ORDER BY id', conn, params=('Sold',))
    
    #df = pd.read_sql('SELECT * FROM "Products" ORDER BY id', conn)
    return df

# grab the amount of money saved (retail_price - defect_price)
def price_diff(conn, product_id: int):
    cursor = conn.cursor()

    cursor.execute('SELECT retail_price, defect_price FROM "Products" WHERE id = %s', (product_id,))
    row = cursor.fetchone()
    retail_price, defect_price = row
    cursor.close()
    return retail_price - defect_price

# grab the weight (in kg) of the amount of textile that will be rescued
def kg_saved(conn, product_id: int):
    cursor = conn.cursor()
    cursor.execute('SELECT weight FROM "Products" WHERE id = %s', (product_id,))
    row = cursor.fetchone()
    cursor.close()
    weight_kg = row[0]
    return weight_kg
    

def reserve_product(conn, product_id):
    cursor = conn.cursor()
    
    # Note the comma to make it a tuple!
    cursor.execute('SELECT status FROM "Products" WHERE id=%s', (product_id,))
    status = cursor.fetchone()[0]
    if status == "Available":
        cursor.execute('UPDATE "Products" SET status = %s WHERE id = %s', ('Reserved', product_id))
        conn.commit()
        cursor.close()
        return "reserved"
    else:
        cursor.close()
        return "already reserved"
    
#locks in the cart, changes all Reserved to Sold
def purchase_product(conn):
    cursor = conn.cursor()
    cursor.execute('UPDATE "Products" SET status = %s WHERE status =%s', ("Sold", "Reserved"))
    conn.commit()
    cursor.close()

def purchase_total(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(defect_price) FROM "Products" WHERE status = %s', ('Sold',))
    result = cursor.fetchone()
    total_defect_price = result[0] if result[0] is not None else 0
    cursor.close()
    return total_defect_price


def purchase_kg_total(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(weight) FROM "Products" WHERE status = %s', ('Sold',))
    result = cursor.fetchone()
    total_weight = result[0] if result[0] is not None else 0
    cursor.close()
    return total_weight


    


