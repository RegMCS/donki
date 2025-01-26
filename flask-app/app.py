from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Dummy data for dashboard
    data_summary = {
        'Total Users': 1500,
        'Active Users': 1200,
        'Total Sales': 500000,
        'Average Rating': 4.5
    }
    
    # Chart data (replace with real chart data)
    chart_data = {
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'values': [10, 25, 40, 35, 50]
    }
    
    return render_template('dashboard.html', data_summary=data_summary, chart_data=chart_data)

if __name__ == "__main__":
    app.run(debug=True)
