class VisualizationAgent:
    def __init__(self):
        pass

    def generate_chart(self, data, chart_type='line'):
        """
        Generates a visual representation of the provided data.

        Parameters:
        - data: The data to visualize.
        - chart_type: The type of chart to generate (e.g., 'line', 'bar', 'pie').

        Returns:
        - A visualization object (e.g., a Plotly figure).
        """
        import plotly.express as px

        if chart_type == 'line':
            fig = px.line(data, x='date', y='value', title='Line Chart')
        elif chart_type == 'bar':
            fig = px.bar(data, x='category', y='value', title='Bar Chart')
        elif chart_type == 'pie':
            fig = px.pie(data, names='category', values='value', title='Pie Chart')
        else:
            raise ValueError("Unsupported chart type: {}".format(chart_type))

        return fig

    def save_chart(self, fig, filename):
        """
        Saves the generated chart to a file.

        Parameters:
        - fig: The visualization object to save.
        - filename: The name of the file to save the chart as.
        """
        fig.write_image(filename)

    def display_chart(self, fig):
        """
        Displays the generated chart in a web browser.

        Parameters:
        - fig: The visualization object to display.
        """
        fig.show()