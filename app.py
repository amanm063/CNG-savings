import streamlit as st
# Set page config
st.set_page_config(
    page_title="CNG Savings Tracker",
    page_icon="🚗",
    layout="wide"
)
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime
from plotly.subplots import make_subplots
from supabase import create_client

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    return create_client(supabase_url, supabase_key)

supabase = init_supabase()

# Function to insert trip data with toast notification
def insert_trip_data(cng_price_per_kg, total_cng_cost, cng_amount, distance, 
                     cng_mileage, petrol_price, petrol_mileage, savings,
                     cng_price_per_km, petrol_price_per_km):
    try:
        data = {
            'date': datetime.now().isoformat(),
            'cng_price_per_kg': cng_price_per_kg,
            'total_cng_cost': total_cng_cost,
            'cng_amount_filled': cng_amount,
            'distance_covered': distance,
            'cng_mileage': cng_mileage,
            'petrol_price': petrol_price,
            'petrol_mileage': petrol_mileage,
            'savings': savings,
            'cng_price_per_km': cng_price_per_km,
            'petrol_price_per_km': petrol_price_per_km
        }
        
        supabase.table('trips').insert(data).execute()
        st.toast('🚗 Trip data saved successfully! Keep saving fuel!', icon='✅')
    except Exception as e:
        st.error(f"Error saving trip data: {e}")
        st.toast('🚨 Failed to save trip data!', icon='❌')

# Function to remove trip data with toast notification
def remove_trip_data(trip_ids):
    try:
        for trip_id in trip_ids:
            supabase.table('trips').delete().eq('id', trip_id).execute()
        st.toast('🚗 Selected entries removed successfully!', icon='🗑️')
    except Exception as e:
        st.error(f"Error removing trip data: {e}")
        st.toast('🚨 Failed to remove entries!', icon='❌')

# Function to get historical data
def get_historical_data():
    try:
        response = supabase.table('trips').select("*").order('date').execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df['date'] = pd.to_datetime(df['date'])
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching historical data: {e}")
        return pd.DataFrame()

def calculate_savings(cng_price_per_kg, total_cng_cost, distance_covered, petrol_price=95, petrol_mileage=18.4):
    try:
        cng_amount_filled = total_cng_cost / cng_price_per_kg
        cng_mileage = distance_covered / cng_amount_filled
        cng_fuel_cost = total_cng_cost
        petrol_fuel_cost = (distance_covered / petrol_mileage) * petrol_price
        savings = petrol_fuel_cost - cng_fuel_cost - 10
        
        # Calculate price per km for both fuels
        cng_price_per_km = total_cng_cost / distance_covered
        petrol_price_per_km = petrol_fuel_cost / distance_covered
        
        return {
            'cng_amount_filled': cng_amount_filled,
            'cng_mileage': cng_mileage,
            'cng_fuel_cost': cng_fuel_cost,
            'petrol_fuel_cost': petrol_fuel_cost,
            'savings': savings,
            'cng_price_per_km': cng_price_per_km,
            'petrol_price_per_km': petrol_price_per_km
        }
    except Exception as e:
        st.error(f"Error calculating savings: {e}")
        return None

def create_visualizations(historical_data):
    # Ensure date is datetime
    historical_data['date'] = pd.to_datetime(historical_data['date'])
    
    # Create a subplot grid of visualizations
    fig = make_subplots(
        rows=3, cols=3, 
        subplot_titles=(
            'Cumulative Savings', 'Savings per Trip', 
            'CNG vs Petrol Cost', 'Distance Covered', 
            'CNG Mileage', 'Petrol Mileage',
            'Price per KM Comparison', 'CNG Price per KM Trend', 'Petrol Price per KM Trend'
        ),
        specs=[[{'type':'scatter'}, {'type':'bar'}, {'type':'scatter'}],
               [{'type':'bar'}, {'type':'scatter'}, {'type':'bar'}],
               [{'type':'bar'}, {'type':'scatter'}, {'type':'scatter'}]]
    )

    # Car icon markers
    car_markers = {
        'green': dict(symbol='triangle-up', size=10, color='green', line=dict(width=2, color='darkgreen')),
        'red': dict(symbol='triangle-up', size=10, color='red', line=dict(width=2, color='darkred'))
    }

    # 1. Cumulative Savings Line Chart
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'], 
            y=historical_data['savings'].cumsum(), 
            mode='lines+markers',
            name='Cumulative Savings',
            line=dict(color='#4CAF50', width=3),
            marker=car_markers['green']
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
            marker=car_markers['green']
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
            marker=car_markers['red']
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
            marker=car_markers['green']
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

    # 7. Price per KM Comparison (Bar Chart)
    fig.add_trace(
        go.Bar(
            name='CNG ₹/km',
            x=historical_data['date'].dt.strftime('%Y-%m-%d'),
            y=historical_data['cng_price_per_km'],
            marker_color='green'
        ),
        row=3, col=1
    )
    fig.add_trace(
        go.Bar(
            name='Petrol ₹/km',
            x=historical_data['date'].dt.strftime('%Y-%m-%d'),
            y=historical_data['petrol_price_per_km'],
            marker_color='red'
        ),
        row=3, col=1
    )

    # 8. CNG Price per KM Trend (Area Chart)
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'],
            y=historical_data['cng_price_per_km'],
            fill='tozeroy',
            name='CNG ₹/km Trend',
            line=dict(color='green', width=2),
            marker=car_markers['green']
        ),
        row=3, col=2
    )

    # 9. Petrol Price per KM Trend (Area Chart)
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'],
            y=historical_data['petrol_price_per_km'],
            fill='tozeroy',
            name='Petrol ₹/km Trend',
            line=dict(color='red', width=2),
            marker=car_markers['red']
        ),
        row=3, col=3
    )

    # Update layout
    fig.update_layout(
        height=1200,
        width=1200,
        title_text="CNG Savings & Performance Dashboard",
        template='plotly_dark',
        showlegend=True,
        title_font_size=20,
        barmode='group'
    )

    return fig

def main():
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
            # Save trip to database
            insert_trip_data(
                cng_price_per_kg, 
                total_cng_cost, 
                result['cng_amount_filled'], 
                distance_covered, 
                result['cng_mileage'], 
                petrol_price, 
                petrol_mileage, 
                result['savings'],
                result['cng_price_per_km'],
                result['petrol_price_per_km']
            )
            
            # Display results
            st.header('Trip Analysis')
            
            # Metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric('CNG Amount Filled', f'{result["cng_amount_filled"]:.2f} kg')
            col2.metric('CNG Mileage', f'{result["cng_mileage"]:.2f} km/kg')
            col3.metric('Trip Savings', f'₹{result["savings"]:.2f}')
            col4.metric('CNG Price/km', f'₹{result["cng_price_per_km"]:.2f}')
            col5.metric('Petrol Price/km', f'₹{result["petrol_price_per_km"]:.2f}')
    
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
                "savings": st.column_config.NumberColumn("Savings (₹)", format="%.2f"),
                "cng_price_per_km": st.column_config.NumberColumn("CNG ₹/km", format="%.2f"),
                "petrol_price_per_km": st.column_config.NumberColumn("Petrol ₹/km", format="%.2f")
            }
        )
        
# Get rows to remove
        rows_to_remove = edited_df[edited_df['remove']]['id'].tolist()
        
        # Remove button
        if st.button('Remove Selected Entries'):
            if rows_to_remove:
                remove_trip_data(rows_to_remove)
                st.rerun()
        
        # Additional Metrics Section
        st.header('Overall Analysis')
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            avg_cng_price = historical_data['cng_price_per_km'].mean()
            st.metric('Average CNG Price/km', f'₹{avg_cng_price:.2f}')
            
        with metric_col2:
            avg_petrol_price = historical_data['petrol_price_per_km'].mean()
            st.metric('Average Petrol Price/km', f'₹{avg_petrol_price:.2f}')
            
        with metric_col3:
            price_difference = avg_petrol_price - avg_cng_price
            st.metric('Average Price Difference/km', f'₹{price_difference:.2f}')
            
        with metric_col4:
            total_distance = historical_data['distance_covered'].sum()
            st.metric('Total Distance Covered', f'{total_distance:.1f} km')
        
        # Plotly Visualizations
        st.header('Detailed Visualizations')
        if st.button('Generate Detailed Visualizations'):
            fig = create_visualizations(historical_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional single-chart visualizations
            st.subheader('Price per KM Comparison Over Time')
            price_comparison_fig = go.Figure()
            price_comparison_fig.add_trace(
                go.Scatter(
                    x=historical_data['date'],
                    y=historical_data['cng_price_per_km'],
                    name='CNG ₹/km',
                    line=dict(color='green', width=2),
                    mode='lines+markers'
                )
            )
            price_comparison_fig.add_trace(
                go.Scatter(
                    x=historical_data['date'],
                    y=historical_data['petrol_price_per_km'],
                    name='Petrol ₹/km',
                    line=dict(color='red', width=2),
                    mode='lines+markers'
                )
            )
            price_comparison_fig.update_layout(
                template='plotly_dark',
                height=500,
                title='CNG vs Petrol Price per KM Trend',
                xaxis_title='Date',
                yaxis_title='Price per KM (₹)',
                showlegend=True
            )
            st.plotly_chart(price_comparison_fig, use_container_width=True)
            
            # Savings Distribution
            st.subheader('Savings Distribution')
            savings_fig = px.histogram(
                historical_data,
                x='savings',
                nbins=20,
                title='Distribution of Savings per Trip',
                template='plotly_dark'
            )
            savings_fig.update_layout(
                xaxis_title='Savings (₹)',
                yaxis_title='Number of Trips',
                showlegend=False
            )
            st.plotly_chart(savings_fig, use_container_width=True)
            
    else:
        st.write("No trip history available yet.")
        
    # Footer
    st.markdown('---')
    st.markdown('Built with Streamlit by Aman🎈 | Track your CNG savings and contribute to a greener future 🌱')

if __name__ == '__main__':
    main()