import plotly.express as px
import plotly.io as pio
import os

def create_html_visualization(plot, last_modification):
    """
    Creates an HTML file to visualize a Plotly line plot.

    Parameters:
    - plot: A Plotly figure object (e.g., from px.line).
    - last_modification: A string representing the last modification date.
    """
    # Define the enhanced HTML template
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Line Plot Visualization</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
                color: #333;
            }
            .navbar {
                background-color: #2c3e50;
                padding: 10px;
                color: white;
                text-align: center;
            }
            .container {
                max-width: 1200px;
                margin: 20px auto;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
                font-weight: 500;
            }
            .plot-container {
                background-color: white;
                padding: 15px;
                border-radius: 8px;
            }
            .footer {
                text-align: center;
                padding: 10px;
                background-color: #2c3e50;
                color: white;
                position: fixed;
                width: 100%;
                bottom: 0;
            }
            .last-modification {
                text-align: left;
                font-size: 0.9em;
                color: #666;
                margin-top: 10px;
            }
            @media (max-width: 768px) {
                .container {
                    margin: 10px;
                    padding: 15px;
                }
            }
        </style>
    </head>
    <body>
        <div class="navbar">
            <h2>Data Visualization Dashboard</h2>
        </div>
        <div class="container">
            <h1>Line Plot Visualization</h1>
            <div class="plot-container">
                {{ plot_div }}
            </div>
            <div class="last-modification">
                Last modified: {{ last_modification }}
            </div>
        </div>
        <div class="footer">
            &copy; 2024 Data Visualization Inc.
        </div>
    </body>
    </html>
    """

    # Convert the Plotly figure to a div
    plot_div = pio.to_html(plot, full_html=False)

    # Replace the placeholders in the template with the plot div and last modification date
    html_content = html_template.replace('{{ plot_div }}', plot_div)
    html_content = html_content.replace('{{ last_modification }}', last_modification)

    return html_content
if __name__ == "__main__":
    df = px.data.gapminder().query("country=='Canada'")
    fig = px.line(df, x='year', y='gdpPercap', title='GDP per Capita in Canada')
    last_modification = "2024-01-01"
    html_content = create_html_visualization(fig, last_modification)
    with open('visualization.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
