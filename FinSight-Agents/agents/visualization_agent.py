import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class VisualizationAgent:
    def __init__(self):
        # Get the root directory (one level up from agents)
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        root_dir = os.path.abspath(os.path.join(script_dir, ".."))
        self.save_dir = os.path.join(root_dir, 'FinSight-Agents', 'data/processed')
        os.makedirs(self.save_dir, exist_ok=True)

    def bar_chart_with_labels(self, data: pd.DataFrame, x, y, title=None, filename='bar_chart.png', sort=True, palette='viridis'):
        plt.figure(figsize=(12, 7))
        plot_data = data.copy()
        if sort:
            plot_data = plot_data.sort_values(by=y, ascending=False)
        ax = sns.barplot(data=plot_data, x=x, y=y, hue=x, palette=palette, legend=False)
        plt.title(title or f"{y} by {x}")
        plt.ylabel(y)
        plt.xlabel(x)
        plt.xticks(rotation=30)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        # Add value labels
        for p in ax.patches:
            ax.annotate(f"{p.get_height():.0f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', fontsize=9, color='black', xytext=(0, 5), textcoords='offset points')
        plt.tight_layout()
        save_path = os.path.join(self.save_dir, filename)
        plt.savefig(save_path)
        plt.close()
        print(f"Enhanced bar chart saved to {save_path}")

    def pie_chart_with_counts(self, data: pd.DataFrame, label_col, value_col, title=None, filename='pie_chart.png'):
        plt.figure(figsize=(8, 8))
        explode = [0.05] * len(data)
        plt.pie(
            data[value_col],
            labels=[f"{row[label_col]} ({row[value_col]})" for _, row in data.iterrows()],
            autopct='%1.1f%%',
            startangle=140,
            explode=explode,
            shadow=True
        )
        plt.title(title or f"{label_col} Distribution")
        plt.tight_layout()
        save_path = os.path.join(self.save_dir, filename)
        plt.savefig(save_path)
        plt.close()
        print(f"Enhanced pie chart saved to {save_path}")

    def generate_chart(self, data: pd.DataFrame, chart_type='line', x=None, y=None, hue=None, title=None, filename='chart.png'):
        plt.figure(figsize=(10, 6))
        if chart_type == 'line':
            sns.lineplot(data=data, x=x, y=y, hue=hue)
        elif chart_type == 'bar':
            sns.barplot(data=data, x=x, y=y, hue=hue)
        elif chart_type == 'pie':
            plt.pie(data[y], labels=data[x], autopct='%1.1f%%', startangle=140)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        if title:
            plt.title(title)
        plt.tight_layout()
        save_path = os.path.join(self.save_dir, filename)
        plt.savefig(save_path)
        plt.close()
        print(f"Chart saved to {save_path}")

    def display_chart(self, data: pd.DataFrame, chart_type='line', x=None, y=None, hue=None, title=None):
        plt.figure(figsize=(10, 6))
        if chart_type == 'line':
            sns.lineplot(data=data, x=x, y=y, hue=hue)
        elif chart_type == 'bar':
            sns.barplot(data=data, x=x, y=y, hue=hue)
        elif chart_type == 'pie':
            plt.pie(data[y], labels=data[x], autopct='%1.1f%%', startangle=140)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        if title:
            plt.title(title)
        plt.tight_layout()
        plt.show()

# Standalone test
if __name__ == "__main__":
    df = pd.DataFrame({
        'Stock': ['AAPL', 'GOOGL', 'TSLA'],
        'Close': [196.4, 174.6, 325.3],
        'Sentiment': ['Positive', 'Positive', 'Positive'],
        'Count': [7, 7, 5]
    })

    agent = VisualizationAgent()
    # Enhanced bar chart
    agent.bar_chart_with_labels(df, x='Stock', y='Close', title='Latest Close Prices', filename='close_prices_seaborn.png')
    # Enhanced pie chart
    sentiment_counts = df.groupby('Sentiment').size().reset_index(name='Count')
    agent.pie_chart_with_counts(sentiment_counts, label_col='Sentiment', value_col='Count', title='Sentiment Distribution', filename='sentiment_pie_seaborn.png')
    # Standard line chart for demo
    agent.generate_chart(df, chart_type='line', x='Stock', y='Close', title='Stock Close Line', filename='close_line_seaborn.png')