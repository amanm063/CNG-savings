import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime
from plotly.subplots import make_subplots

# Set page config with car-themed icon and title
st.set_page_config(
    page_title="CNG Savings Tracker",
    page_icon="🚗",
    layout="wide"
)

# Database Initialization
def init_database():
    conn = sqlite3.connect('cng_savings.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        cng_price_per_kg REAL,
        total_cng_cost REAL,
        cng_amount_filled REAL,
        distance_covered REAL,
        cng_mileage REAL,
        petrol_price REAL,
        petrol_mileage REAL,
        savings REAL
    )''')
    conn.commit()
    conn.close()

# Function to insert trip data with toast notification
def insert_trip_data(cng_price_per_kg, total_cng_cost, cng_amount, distance, 
                     cng_mileage, petrol_price, petrol_mileage, savings):
    try:
        conn = sqlite3.connect('cng_savings.db')
        c = conn.cursor()
        c.execute('''INSERT INTO trips (
            date, 
            cng_price_per_kg, 
            total_cng_cost, 
            cng_amount_filled, 
            distance_covered,
            cng_mileage,
            petrol_price,
            petrol_mileage,
            savings
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            cng_price_per_kg,
            total_cng_cost,
            cng_amount,
            distance,
            cng_mileage,
            petrol_price,
            petrol_mileage,
            savings
        ))
        conn.commit()
        
        # Toast notification using st.toast
        st.toast('🚗 Trip data saved successfully! Keep saving fuel!', icon='✅')
    except Exception as e:
        st.error(f"Error saving trip data: {e}")
        st.toast('🚨 Failed to save trip data!', icon='❌')
    finally:
        conn.close()

# Function to remove trip data with toast notification
def remove_trip_data(trip_ids):
    try:
        conn = sqlite3.connect('cng_savings.db')
        c = conn.cursor()
        c.execute("DELETE FROM trips WHERE id IN ({})".format(
            ','.join(['?']*len(trip_ids)), 
        ), trip_ids)
        conn.commit()
        st.toast('🚗 Selected entries removed successfully!', icon='🗑️')
    except Exception as e:
        st.error(f"Error removing trip data: {e}")
        st.toast('🚨 Failed to remove entries!', icon='❌')
    finally:
        conn.close()

# Function to get historical data
def get_historical_data():
    try:
        conn = sqlite3.connect('cng_savings.db')
        df = pd.read_sql_query("SELECT * FROM trips ORDER BY date", conn)
        df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        st.error(f"Error fetching historical data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()
    return df

def calculate_savings(cng_price_per_kg, total_cng_cost, distance_covered, petrol_price, petrol_mileage=18.4):
    try:
        cng_amount_filled = total_cng_cost / cng_price_per_kg
        cng_mileage = distance_covered / cng_amount_filled
        cng_fuel_cost = total_cng_cost
        petrol_fuel_cost = (distance_covered / petrol_mileage) * petrol_price
        savings = petrol_fuel_cost - cng_fuel_cost - 10
        
        return {
            'cng_amount_filled': cng_amount_filled,
            'cng_mileage': cng_mileage,
            'cng_fuel_cost': cng_fuel_cost,
            'petrol_fuel_cost': petrol_fuel_cost,
            'savings': savings
        }
    except Exception as e:
        st.error(f"Error calculating savings: {e}")
        return None

def create_visualizations(historical_data):
    # Ensure date is datetime
    historical_data['date'] = pd.to_datetime(historical_data['date'])
    
    # Create a subplot grid of visualizations
    fig = make_subplots(
        rows=2, cols=3, 
        subplot_titles=(
            'Cumulative Savings', 'Savings per Trip', 
            'CNG vs Petrol Cost', 'Distance Covered', 
            'CNG Mileage', 'Petrol Mileage'
        ),
        specs=[[{'type':'scatter'}, {'type':'bar'}, {'type':'scatter'}],
               [{'type':'bar'}, {'type':'scatter'}, {'type':'bar'}]]
    )

    # Car icon markers for scatter plots (red for petrol, green for CNG)
    red_car_marker = dict(
        symbol='triangle-up',  # Alternative to car marker
        size=10,
        color='red',
        line=dict(width=2, color='darkred')
)
    green_car_marker = dict(
        symbol='triangle-up',  # Alternative to car marker
        size=10,
        color='green',
        line=dict(width=2, color='darkgreen')
)

    # 1. Cumulative Savings Line Chart
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'], 
            y=historical_data['savings'].cumsum(), 
            mode='lines+markers',
            name='Cumulative Savings',
            line=dict(color='#4CAF50', width=3),
            marker=green_car_marker
        ),
        row=1, col=1
    )

    # 2. Savings per Trip Bar Chart
    fig.add_trace(
        go.Bar(
            x=historical_data['date'].dt.strftime('%Y-%m-%d'), 
            y=historical_data['savings'], 
            name='Trip Savings',
            marker_color='#4CAF50'
        ),
        row=1, col=2
    )

    # 3. CNG vs Petrol Cost
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'], 
            y=historical_data['cng_price_per_kg'], 
            mode='lines+markers', 
            name='CNG Price',
            line=dict(color='green'),
            marker=green_car_marker
        ),
        row=1, col=3
    )
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'], 
            y=historical_data['petrol_price'], 
            mode='lines+markers', 
            name='Petrol Price',
            line=dict(color='red'),
            marker=red_car_marker
        ),
        row=1, col=3
    )

    # 4. Distance Covered Bar Chart
    fig.add_trace(
        go.Bar(
            x=historical_data['date'].dt.strftime('%Y-%m-%d'), 
            y=historical_data['distance_covered'], 
            name='Distance Covered',
            marker_color='#4CAF50'
        ),
        row=2, col=1
    )

    # 5. CNG Mileage Scatter
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'], 
            y=historical_data['cng_mileage'], 
            mode='lines+markers',
            name='CNG Mileage',
            line=dict(color='green'),
            marker=green_car_marker
        ),
        row=2, col=2
    )

    # 6. Petrol Mileage Bar Chart
    fig.add_trace(
        go.Bar(
            x=historical_data['date'].dt.strftime('%Y-%m-%d'), 
            y=historical_data['petrol_mileage'], 
            name='Petrol Mileage',
            marker_color='red'
        ),
        row=2, col=3
    )

    # Update layout for dark theme and readability
    fig.update_layout(
        height=800, 
        width=1200,
        title_text="CNG Savings & Performance Dashboard",
        template='plotly_dark',
        showlegend=True,
        title_font_size=20
    )

    return fig

def main():
    # Initialize database
    init_database()

    st.title('🚗 CNG Savings Calculator')
    
    # Input section
    st.header('Trip Details')
    
    # Create columns for inputs
    col1, col2 = st.columns(2)
    
    with col1:
        # CNG Details
        st.subheader('CNG Details')
        cng_price_per_kg = st.number_input('CNG Price per kg (₹)', min_value=0.0, step=0.1)
        total_cng_cost = st.number_input('Total CNG Filling Cost (₹)', min_value=0.0, step=10.0)
        distance_covered = st.number_input('Distance Covered (km)', min_value=0.0, step=1.0)
    
    with col2:
        # Petrol Details
        st.subheader('Petrol Comparison')
        petrol_price = st.number_input('Current Petrol Price (₹/liter)', min_value=0.0, step=1.0)
        petrol_mileage = st.number_input('Petrol Mileage (km/l)', min_value=0.0, step=0.1, value=18.4)
    
    # Calculate button
    if st.button('Calculate Savings'):
        result = calculate_savings(
            cng_price_per_kg, 
            total_cng_cost, 
            distance_covered, 
            petrol_price, 
            petrol_mileage
        )
        
        if result is not None:
            # Save trip to database and show toast
            insert_trip_data(
                cng_price_per_kg, 
                total_cng_cost, 
                result['cng_amount_filled'], 
                distance_covered, 
                result['cng_mileage'], 
                petrol_price, 
                petrol_mileage, 
                result['savings']
            )
            
            # Display results
            st.header('Trip Analysis')
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric('CNG Amount Filled', f'{result["cng_amount_filled"]:.2f} kg')
            col2.metric('CNG Mileage', f'{result["cng_mileage"]:.2f} km/kg')
            col3.metric('Trip Savings', f'₹{result["savings"]:.2f}')
    
    # Historical Data Section
    st.header('Trip History')
    
    historical_data = get_historical_data()
    
    if not historical_data.empty:
        total_savings = historical_data['savings'].sum()
        st.metric('Total Cumulative Savings', f'₹{total_savings:.2f}')
        
        # Add a copy of the dataframe with a remove column
        df_display = historical_data.copy()
        df_display['remove'] = False
        
        # Editable data editor with remove functionality
        edited_df = st.data_editor(
            df_display, 
            num_rows="dynamic",
            column_config={
                "remove": st.column_config.CheckboxColumn("Remove"),
                "id": "ID",
                "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD HH:mm:ss"),
                "cng_price_per_kg": st.column_config.NumberColumn("CNG Price/kg (₹)", format="%.2f"),
                "total_cng_cost": st.column_config.NumberColumn("Total CNG Cost (₹)", format="%.2f"),
                "cng_amount_filled": st.column_config.NumberColumn("CNG Amount (kg)", format="%.2f"),
                "distance_covered": st.column_config.NumberColumn("Distance (km)", format="%.2f"),
                "cng_mileage": st.column_config.NumberColumn("CNG Mileage (km/kg)", format="%.2f"),
                "petrol_price": st.column_config.NumberColumn("Petrol Price (₹/l)", format="%.2f"),
                "petrol_mileage": st.column_config.NumberColumn("Petrol Mileage (km/l)", format="%.2f"),
                "savings": st.column_config.NumberColumn("Savings (₹)", format="%.2f")
}
        )
        
        # Get rows to remove
        rows_to_remove = edited_df[edited_df['remove']]['id'].tolist()
        
        # Remove button
        if st.button('Remove Selected Entries'):
            if rows_to_remove:
                remove_trip_data(rows_to_remove)
                st.rerun()
        
        # Plotly Visualizations
        if st.button('Generate Detailed Visualizations'):
            fig = create_visualizations(historical_data)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No trip history available yet.")

if __name__ == '__main__':
    main()