"""
GLOBAL DEVELOPMENT INSIGHTS
Main Flask Application
"""

import os
from utils.country_validator import get_all_countries
from flask import Flask, render_template, request, redirect, url_for
from utils.data_loader import load_historical_data, load_future_data, load_master_data
from utils.country_validator import validate_country
from utils.chart_generator import (
    generate_historical_chart,
    generate_forecast_chart,
    generate_multi_indicator_chart
)

app = Flask(__name__)
app.config['CHART_FOLDER'] = os.path.join('static', 'charts')

# Ensure chart directory exists
os.makedirs(app.config['CHART_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    """Home page with search and global stats."""
    try:
        hist_df = load_historical_data()
        total_countries = hist_df['Country Name'].nunique()
        latest_year = int(hist_df['Year'].max())
        avg_dev_score = round(hist_df[hist_df['Year'] == latest_year]['Development_Score'].mean(), 2)

        # Development level distribution for latest year
        latest_data = hist_df[hist_df['Year'] == latest_year]
        dev_counts = latest_data['Development_Level'].value_counts().to_dict()

        underdeveloped = dev_counts.get('Underdeveloped', 0)
        developing = dev_counts.get('Developing', 0)
        highly_developed = dev_counts.get('Highly Developed', 0)

        countries = get_all_countries()


        return render_template('index.html',
                               total_countries=total_countries,
                               latest_year=latest_year,
                               avg_dev_score=avg_dev_score,
                               underdeveloped=underdeveloped,
                               developing=developing,
                               highly_developed=highly_developed,
                               all_countries=countries)
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search for a country."""
    if request.method == 'POST':
        country_name = request.form.get('country_name', '').strip()
    else:
        country_name = request.args.get('country_name', '').strip()

    if not country_name:
        return redirect(url_for('index'))

    return redirect(url_for('country_dashboard', country_name=country_name))


@app.route('/country/<country_name>', methods=['GET', 'POST'])
def country_dashboard(country_name):
    """Full country analysis dashboard."""
    try:
        hist_df = load_historical_data()
        future_df = load_future_data()
        master_df = load_master_data()
        print(master_df.columns.tolist())

        # Validate country in historical data
        is_valid, matched_name = validate_country(hist_df, country_name)
        if not is_valid:
            return render_template('error.html',
                                   error=f"Country '{country_name}' Not Available",
                                   country_name=country_name)

        country_name = matched_name
        country_hist = hist_df[hist_df['Country Name'] == country_name].sort_values('Year')
        country_master = master_df[master_df['Country Name'] == country_name].sort_values('Year')

        # Check if country exists in future dataset
        future_valid, _ = validate_country(future_df, country_name)
        country_future = None
        if future_valid:
            country_future = future_df[future_df['Country Name'] == country_name].sort_values('Year')

        # Latest historical stats
        latest_row = country_hist.iloc[-1]
        latest_master = country_master.iloc[-1]
        latest_year = int(latest_row['Year'])
        current_gdp = round(float(latest_master['GDP']), 2) if 'GDP' in latest_master else 'N/A'
        current_dev_score = round(float(latest_master['Development_Score']), 2)
        current_dev_level = latest_master['Development_Level']
        current_inflation = round(float(latest_master['Inflation']), 2) if 'Inflation' in latest_master else 'N/A'
        current_life_exp = round(float(latest_master['Life_Expectancy']), 2) if 'Life_Expectancy' in latest_master else 'N/A'
        current_literacy = round(float(latest_master['Literacy_Rate']), 2) if 'Literacy_Rate' in latest_master else 'N/A'
        current_internet = round(float(latest_master['Internet_Users']), 2) if 'Internet_Users' in latest_master else 'N/A'
        current_poverty = round(float(latest_master['Poverty']), 2) if 'Poverty' in latest_master else 'N/A'
        current_unemployment = round(float(latest_master['Unemployment']), 2) if 'Unemployment' in latest_master else 'N/A'

        # Forecast stats
        forecast_gdp = 'N/A'
        forecast_dev_score = 'N/A'
        forecast_dev_level = 'N/A'
        if country_future is not None and len(country_future) > 0:
            last_forecast = country_future.iloc[-1]
            forecast_gdp = round(float(last_forecast['GDP_Per_Capita']), 2)
            forecast_dev_score = round(float(last_forecast['Development_Score']), 2)
            forecast_dev_level = last_forecast['Development_Level']

        # Handle form selections
        selected_metric = request.form.get('metric', 'Development_Score') if request.method == 'POST' else 'Development_Score'
        selected_multi = request.form.getlist('multi_metrics') if request.method == 'POST' else ['GDP', 'Development_Score']
        selected_forecast_metric = request.form.get('forecast_metric', 'Development_Score') if request.method == 'POST' else 'Development_Score'
        selected_future_year = request.form.get('future_year', '2030') if request.method == 'POST' else '2030'
        form_action = request.form.get('form_action', '') if request.method == 'POST' else ''

        # Default multi metrics if empty
        if not selected_multi:
            selected_multi = ['GDP', 'Development_Score']

        available_metrics = ['GDP', 'Inflation', 'Internet_Users', 'Life_Expectancy',
                             'Literacy_Rate', 'Poverty', 'Unemployment', 'Development_Score']

        # Generate charts
        hist_chart = None
        multi_chart = None
        forecast_chart = None
        future_year_data = None

        # Always generate default or selected charts
        hist_chart = generate_historical_chart(country_master, selected_metric, country_name)
        multi_chart = generate_multi_indicator_chart(country_master, selected_multi, country_name)

        if country_future is not None:
            forecast_chart = generate_forecast_chart(country_future, selected_forecast_metric, country_name)

            # Future year development index
            future_year_int = int(selected_future_year)
            future_row = country_future[country_future['Year'] == future_year_int]
            if len(future_row) > 0:
                row = future_row.iloc[0]
                future_year_data = {
                    'year': future_year_int,
                    'dev_score': round(float(row['Development_Score']), 2),
                    'dev_level': row['Development_Level'],
                    'gdp_per_capita': round(float(row['GDP_Per_Capita']), 2)
                }

        # Future years for dropdown
        future_years = list(range(2025, 2041)) if country_future is not None else []

        countries = get_all_countries()

        return render_template('country.html',
                               all_countries=countries,
                               country_name=country_name,
                               latest_year=latest_year,
                               current_gdp=current_gdp,
                               current_dev_score=current_dev_score,
                               current_dev_level=current_dev_level,
                               current_inflation=current_inflation,
                               current_life_exp=current_life_exp,
                               current_literacy=current_literacy,
                               current_internet=current_internet,
                               current_poverty=current_poverty,
                               current_unemployment=current_unemployment,
                               forecast_gdp=forecast_gdp,
                               forecast_dev_score=forecast_dev_score,
                               forecast_dev_level=forecast_dev_level,
                               available_metrics=available_metrics,
                               selected_metric=selected_metric,
                               selected_multi=selected_multi,
                               selected_forecast_metric=selected_forecast_metric,
                               selected_future_year=selected_future_year,
                               hist_chart=hist_chart,
                               multi_chart=multi_chart,
                               forecast_chart=forecast_chart,
                               future_year_data=future_year_data,
                               future_years=future_years,
                               has_future_data=(country_future is not None))

    except Exception as e:
        import traceback
        traceback.print_exc()
        return render_template('error.html', error=str(e), country_name=country_name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page Not Found (404)"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Internal Server Error (500)"), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
