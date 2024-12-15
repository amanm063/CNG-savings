# 🚗 CNG Savings Tracker

## 🌟 Motivation and Necessity

In an era of rising fuel costs and environmental consciousness, the CNG Savings Tracker was developed to help vehicle owners:

1. **Financial Awareness**: Understand the real economic benefits of switching to Compressed Natural Gas (CNG)
2. **Comparative Analysis**: Directly compare fuel costs between CNG and traditional petrol
3. **Personal Fuel Efficiency Tracking**: Monitor and improve vehicle performance over time

### Why CNG?
- **Cost-Effective**: Typically cheaper than petrol
- **Environmentally Friendly**: Lower carbon emissions
- **Growing Infrastructure**: Increasing CNG stations make it more viable

## 🛠 Features

- **Real-time Savings Calculation**
- **Detailed Trip History**
- **Comprehensive Visualizations**
  - Cumulative Savings
  - Trip-wise Savings
  - Fuel Price Trends
  - Mileage Comparisons

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Streamlit
- Pandas
- Plotly
- SQLite3

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/[YourUsername]/cng-savings-tracker.git
   cd cng-savings-tracker
   ```

2. **Create Virtual Environment** (Optional but Recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install streamlit pandas plotly
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## 📊 How to Use

### Entering Trip Details
1. Input CNG Details
   - CNG Price per kg
   - Total CNG Filling Cost
   - Distance Covered

2. Input Petrol Comparison Details
   - Current Petrol Price
   - Your Vehicle's Petrol Mileage

3. Click "Calculate Savings"

### Trip History
- View all your previous trips
- Remove entries if needed
- Generate detailed visualizations

## 🔍 How Savings are Calculated

The app calculates savings by:
1. Computing CNG fuel cost for the trip
2. Estimating equivalent petrol fuel cost
3. Subtracting CNG cost from petrol cost
4. Accounting for a small maintenance buffer (₹10)

## 🤝 Contributing

1. Fork the Repository
2. Create a Feature Branch
   ```bash
   git checkout -b feature/amazing-improvement
   ```
3. Commit Your Changes
   ```bash
   git commit -m 'Add some amazing improvement'
   ```
4. Push to Branch
   ```bash
   git push origin feature/amazing-improvement
   ```
5. Open a Pull Request

## 🔒 Customization Tips

- Adjust default petrol mileage
- Modify visualization styles
- Add more detailed reporting features
- Implement user authentication

## 📈 Future Roadmap
- Mobile App Version
- Cloud Sync
- Advanced Analytics
- Multi-Vehicle Support

## 👨‍💻 About the Developer
Aman Malik
---

**Happy Saving, Happy Driving!** 🚗💨