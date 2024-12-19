import streamlit as st
# Set page config
st.set_page_config(
    page_title="FuelWise - CNG Savings Tracker",
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
    
    # Create a subplot grid with more vertical spacing
    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=(
            'Cumulative Savings', 'Savings per Trip', 
            'CNG vs Petrol Cost', 'Distance Covered', 
            'CNG Mileage', 'Petrol Mileage',
            'Price per KM Comparison', 'CNG Price per KM', 'Petrol Price per KM'
        ),
        specs=[[{'type':'scatter'}, {'type':'bar'}, {'type':'scatter'}],
               [{'type':'bar'}, {'type':'scatter'}, {'type':'bar'}],
               [{'type':'bar'}, {'type':'scatter'}, {'type':'scatter'}]],
        vertical_spacing=0.12,  # Increased vertical spacing
        horizontal_spacing=0.08  # Adjusted horizontal spacing
    )

    # Car icon markers
    car_markers = {
        'green': dict(symbol='triangle-up', size=8, color='green', line=dict(width=1, color='darkgreen')),
        'red': dict(symbol='triangle-up', size=8, color='red', line=dict(width=1, color='darkred'))
    }

    # Function to format dates for x-axis
    def format_date(date):
        return date.strftime('%d-%b')

    # Add traces with optimized configurations
    # 1. Cumulative Savings Line Chart
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'].apply(format_date), 
            y=historical_data['savings'].cumsum(), 
            mode='lines+markers',
            name='Cumulative',
            line=dict(color='#4CAF50', width=2),
            marker=car_markers['green']
        ),
        row=1, col=1
    )

    # 2. Savings per Trip Bar Chart
    fig.add_trace(
        go.Bar(
            x=historical_data['date'].apply(format_date), 
            y=historical_data['savings'], 
            name='Savings',
            marker_color='#4CAF50'
        ),
        row=1, col=2
    )

    # 3. CNG vs Petrol Cost
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'].apply(format_date), 
            y=historical_data['cng_price_per_kg'], 
            mode='lines+markers', 
            name='CNG',
            line=dict(color='green', width=2),
            marker=car_markers['green']
        ),
        row=1, col=3
    )
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'].apply(format_date), 
            y=historical_data['petrol_price'], 
            mode='lines+markers', 
            name='Petrol',
            line=dict(color='red', width=2),
            marker=car_markers['red']
        ),
        row=1, col=3
    )

    # 4. Distance Covered Bar Chart
    fig.add_trace(
        go.Bar(
            x=historical_data['date'].apply(format_date), 
            y=historical_data['distance_covered'], 
            name='Distance',
            marker_color='#4CAF50'
        ),
        row=2, col=1
    )

    # 5. CNG Mileage Scatter
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'].apply(format_date), 
            y=historical_data['cng_mileage'], 
            mode='lines+markers',
            name='CNG km/kg',
            line=dict(color='green', width=2),
            marker=car_markers['green']
        ),
        row=2, col=2
    )

    # 6. Petrol Mileage Bar Chart
    fig.add_trace(
        go.Bar(
            x=historical_data['date'].apply(format_date), 
            y=historical_data['petrol_mileage'], 
            name='Petrol km/l',
            marker_color='red'
        ),
        row=2, col=3
    )

    # 7. Price per KM Comparison
    fig.add_trace(
        go.Bar(
            name='CNG/km',
            x=historical_data['date'].apply(format_date),
            y=historical_data['cng_price_per_km'],
            marker_color='green'
        ),
        row=3, col=1
    )
    fig.add_trace(
        go.Bar(
            name='Petrol/km',
            x=historical_data['date'].apply(format_date),
            y=historical_data['petrol_price_per_km'],
            marker_color='red'
        ),
        row=3, col=1
    )

    # 8. CNG Price per KM Trend
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'].apply(format_date),
            y=historical_data['cng_price_per_km'],
            fill='tozeroy',
            name='CNG/km',
            line=dict(color='green', width=2),
            marker=car_markers['green']
        ),
        row=3, col=2
    )

    # 9. Petrol Price per KM Trend
    fig.add_trace(
        go.Scatter(
            x=historical_data['date'].apply(format_date),
            y=historical_data['petrol_price_per_km'],
            fill='tozeroy',
            name='Petrol/km',
            line=dict(color='red', width=2),
            marker=car_markers['red']
        ),
        row=3, col=3
    )

    # Update layout with mobile-friendly configurations
    fig.update_layout(
        height=1400,  # Increased height for better mobile viewing
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        title=dict(
            text="FuelWise - CNG Savings Dashboard",
            font=dict(size=16)
        ),
        template='plotly_dark',
        margin=dict(l=10, r=10, t=100, b=10)  # Adjusted margins
    )

    # Update axes for better mobile visibility
    fig.update_xaxes(
        tickangle=45,
        tickfont=dict(size=8),
        title_font=dict(size=10),
        title_standoff=5
    )
    fig.update_yaxes(
        tickfont=dict(size=8),
        title_font=dict(size=10),
        title_standoff=5
    )

    # Update subplot titles
    fig.update_annotations(font_size=10)

    return fig

def main():
    st.title('🚗 FuelWise - CNG Savings Calculator')
    
    # Input section with mobile-friendly layout
    st.header('Trip Details')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('CNG Details')
        cng_price_per_kg = st.number_input('CNG Price/kg (₹)', min_value=0.0, step=0.1)
        total_cng_cost = st.number_input('Total CNG Cost (₹)', min_value=0.0, step=10.0)
        distance_covered = st.number_input('Distance (km)', min_value=0.0, step=1.0)
    
    with col2:
        st.subheader('Petrol Details')
        petrol_price = st.number_input('Petrol Price (₹/L)', min_value=0.0, step=1.0)
        petrol_mileage = st.number_input('Petrol Mileage (km/L)', min_value=0.0, step=0.1, value=18.4)
    
    if st.button('Calculate Savings'):
        result = calculate_savings(
            cng_price_per_kg, 
            total_cng_cost, 
            distance_covered, 
            petrol_price, 
            petrol_mileage
        )
        
        if result is not None:
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
            
            st.header('Trip Analysis')
            
            # Responsive metrics layout
            cols = st.columns([1, 1, 1, 1, 1])
            cols[0].metric('CNG (kg)', f"{result['cng_amount_filled']:.1f}")
            cols[1].metric('CNG km/kg', f"{result['cng_mileage']:.1f}")
            cols[2].metric('Savings', f"₹{result['savings']:.0f}")
            cols[3].metric('CNG/km', f"₹{result['cng_price_per_km']:.1f}")
            cols[4].metric('Petrol/km', f"₹{result['petrol_price_per_km']:.1f}")
    
    st.header('Trip History')
    historical_data = get_historical_data()
    
    if not historical_data.empty:
        total_savings = historical_data['savings'].sum()
        st.metric('Total Savings', f'₹{total_savings:.0f}')
        
        df_display = historical_data.copy()
        df_display['remove'] = False
        
        # Mobile-friendly data editor
        edited_df = st.data_editor(
            df_display,
            num_rows="dynamic",
            column_config={
                "remove": st.column_config.CheckboxColumn("❌"),
                "id": "ID",
                "date": st.column_config.DateColumn("Date", format="DD-MMM"),
                "cng_price_per_kg": st.column_config.NumberColumn("CNG/kg", format="%.1f"),
                "total_cng_cost": st.column_config.NumberColumn("Cost", format="%.0f"),
                "cng_amount_filled": st.column_config.NumberColumn("CNG kg", format="%.1f"),
                "distance_covered": st.column_config.NumberColumn("Dist", format="%.0f"),
                "cng_mileage": st.column_config.NumberColumn("km/kg", format="%.1f"),
                "petrol_price": st.column_config.NumberColumn("Pet/L", format="%.1f"),
                "petrol_mileage": st.column_config.NumberColumn("km/L", format="%.1f"),
                "savings": st.column_config.NumberColumn("Save", format="%.0f"),
                "cng_price_per_km": st.column_config.NumberColumn("CNG/km", format="%.1f"),
                "petrol_price_per_km": st.column_config.NumberColumn("Pet/km", format="%.1f")
            },
            hide_index=True
        )
        
        rows_to_remove = edited_df[edited_df['remove']]['id'].tolist()
        
        if st.button('Remove Selected'):
            if rows_to_remove:
                remove_trip_data(rows_to_remove)
                st.rerun()
        
        st.header('Analysis')
        cols = st.columns(4)
        
        with cols[0]:
            avg_cng_price = historical_data['cng_price_per_km'].mean()
            st.metric('Avg CNG/km', f'₹{avg_cng_price:.1f}')
            
        with cols[1]:
            avg_petrol_price = historical_data['petrol_price_per_km'].mean()
            st.metric('Avg Petrol/km', f'₹{avg_petrol_price:.1f}')
            
        with cols[2]:
            price_difference = avg_petrol_price - avg_cng_price
            st.metric('Diff/km', f'₹{price_difference:.1f}')
            
        with cols[3]:
            total_distance = historical_data['distance_covered'].sum()
            st.metric('Total km', f'{total_distance:.0f}')
        
        st.header('Visualizations')
        if st.button('Show Charts'):
            fig = create_visualizations(historical_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Mobile-friendly single charts
            price_comparison_fig = go.Figure()
            price_comparison_fig.add_trace(
                go.Scatter(
                    x=historical_data['date'].apply(lambda x: x.strftime('%d-%b')),
                    y=historical_data['cng_price_per_km'],
                    name='CNG/km',
                    line=dict(color='green', width=2),
                    mode='lines+markers'
                )
            )
            price_comparison_fig.add_trace(
                go.Scatter(
                    x=historical_data['date'].apply(lambda x: x.strftime('%d-%b')),
                    y=historical_data['petrol_price_per_km'],
                    name='Petrol/km',
                    line=dict(color='red', width=2),
                    mode='lines+markers'
                )
            )
            price_comparison_fig.update_layout(
                template='plotly_dark',
                height=400,
                title=dict(
                    text='Price per KM Trend',
                    font=dict(size=14)
                ),
                xaxis=dict(
                    title='Date',
                    tickangle=45,
                    tickfont=dict(size=10)
                ),
                yaxis=dict(
                    title='Price per KM (₹)',
                    tickfont=dict(size=10)
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=10)
                ),
                margin=dict(l=10, r=10, t=50, b=10)
            )
            st.plotly_chart(price_comparison_fig, use_container_width=True)
            
            # Mobile-friendly savings distribution
            savings_fig = px.histogram(
                historical_data,
                x='savings',
                nbins=15,
                title='Savings Distribution',
                template='plotly_dark'
            )
            savings_fig.update_layout(
                height=400,
                title=dict(
                    text='Savings Distribution',
                    font=dict(size=14)
                ),
                xaxis=dict(
                    title='Savings (₹)',
                    tickfont=dict(size=10)
                ),
                yaxis=dict(
                    title='Number of Trips',
                    tickfont=dict(size=10)
                ),
                showlegend=False,
                margin=dict(l=10, r=10, t=50, b=10)
            )
            st.plotly_chart(savings_fig, use_container_width=True)
            
    else:
        st.info("No trip history available yet. Add your first trip to see the analysis!")
        
    # Footer
    st.markdown('---')
    st.markdown(
        '<div style="text-align: center; color: #666;">Built with ❤️ by Aman | '
        'Track your CNG savings and contribute to a greener future 🌱</div>', 
        unsafe_allow_html=True
    )

if __name__ == '__main__':
    main()