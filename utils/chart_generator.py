"""
Chart Generator Utility
Generates Matplotlib PNG charts for historical and forecast data.
"""

import os
import uuid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np

CHART_DIR = os.path.join('static', 'charts')
os.makedirs(CHART_DIR, exist_ok=True)

# ── Palette inspired by the isomorphic dashboard (deep + light blues) ──
BLUE_DARK   = '#1e40af'
BLUE_MED    = '#3b82f6'
BLUE_LIGHT  = '#93c5fd'
BLUE_PALE   = '#dbeafe'
ACCENT_RED  = '#ef4444'
ACCENT_GRN  = '#22c55e'
ACCENT_ORG  = '#f59e0b'
ACCENT_PRP  = '#8b5cf6'
ACCENT_CYN  = '#06b6d4'
ACCENT_PNK  = '#ec4899'
GRID_COLOR  = '#e2e8f0'
TEXT_COLOR  = '#1e293b'
SUBTEXT     = '#64748b'

LINE_COLORS = [BLUE_DARK, BLUE_MED, ACCENT_GRN, ACCENT_ORG,
               ACCENT_PRP, ACCENT_CYN, ACCENT_RED, ACCENT_PNK]

METRIC_LABELS = {
    'GDP':              'GDP (USD)',
    'Inflation':        'Inflation (%)',
    'Internet_Users':   'Internet Users (%)',
    'Life_Expectancy':  'Life Expectancy (years)',
    'Literacy_Rate':    'Literacy Rate (%)',
    'Poverty':          'Poverty Rate (%)',
    'Unemployment':     'Unemployment Rate (%)',
    'Development_Score':'Development Score',
    'GDP_Per_Capita':   'GDP Per Capita (USD)',
}


def _base_fig(figsize=(10, 4.5)):
    """Return a styled figure and axes."""
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.set_facecolor('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(GRID_COLOR)
    ax.spines['bottom'].set_color(GRID_COLOR)
    ax.tick_params(colors=SUBTEXT, labelsize=9)
    ax.yaxis.grid(True, color=GRID_COLOR, linewidth=0.8, linestyle='--')
    ax.set_axisbelow(True)
    return fig, ax


def _save_chart(fig, prefix='chart') -> str:
    """Save figure to chart directory; return URL-safe relative path."""
    # Clean up old charts with same prefix to avoid stale images piling up
    for f in os.listdir(CHART_DIR):
        if f.startswith(prefix + '_'):
            try:
                os.remove(os.path.join(CHART_DIR, f))
            except OSError:
                pass

    filename = f"{prefix}_{uuid.uuid4().hex[:8]}.png"
    path = os.path.join(CHART_DIR, filename)
    fig.savefig(path, dpi=130, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    return filename  # returned value used in url_for('static', filename=...)


def generate_historical_chart(df: pd.DataFrame, metric: str, country: str) -> str:
    """Line chart for a single historical metric over years."""
    if metric not in df.columns:
        return None

    data = df[['Year', metric]].dropna().sort_values('Year')
    if data.empty:
        return None

    fig, ax = _base_fig()
    years = data['Year'].astype(int)
    values = data[metric].astype(float)

    # Gradient fill under line
    ax.fill_between(years, values, alpha=0.12, color=BLUE_MED)
    ax.plot(years, values, color=BLUE_DARK, linewidth=2.5,
            marker='o', markersize=5, markerfacecolor='white',
            markeredgewidth=2, markeredgecolor=BLUE_DARK, zorder=3)

    label = METRIC_LABELS.get(metric, metric.replace('_', ' '))
    ax.set_xlabel('Year', color=SUBTEXT, fontsize=10)
    ax.set_ylabel(label, color=SUBTEXT, fontsize=10)
    ax.set_title(f'{country} — {label} (2014–2024)',
                 color=TEXT_COLOR, fontsize=13, fontweight='bold', pad=12)
    ax.set_xticks(years)
    ax.tick_params(axis='x', rotation=45)

    # Value annotations
    for x, y in zip(years, values):
        ax.annotate(f'{y:,.1f}', (x, y),
                    textcoords='offset points', xytext=(0, 8),
                    ha='center', fontsize=7.5, color=BLUE_DARK)

    fig.tight_layout()
    prefix = f"hist_{country.replace(' ', '_')}_{metric}"
    return _save_chart(fig, prefix)


def generate_forecast_chart(df: pd.DataFrame, metric: str, country: str) -> str:
    """Line chart for a forecast metric (2025–2040)."""
    if metric not in df.columns:
        return None

    data = df[['Year', metric]].dropna().sort_values('Year')
    if data.empty:
        return None

    fig, ax = _base_fig()
    years = data['Year'].astype(int)
    values = data[metric].astype(float)

    # Dashed forecast style
    ax.fill_between(years, values, alpha=0.10, color=ACCENT_GRN)
    ax.plot(years, values, color=ACCENT_GRN, linewidth=2.5,
            linestyle='--', marker='D', markersize=5,
            markerfacecolor='white', markeredgewidth=2,
            markeredgecolor=ACCENT_GRN, zorder=3)

    # Vertical reference line at 2030
    ax.axvline(x=2030, color=ACCENT_ORG, linewidth=1.2,
               linestyle=':', alpha=0.7, label='2030 Milestone')
    ax.legend(fontsize=8, frameon=False)

    label = METRIC_LABELS.get(metric, metric.replace('_', ' '))
    ax.set_xlabel('Year', color=SUBTEXT, fontsize=10)
    ax.set_ylabel(label, color=SUBTEXT, fontsize=10)
    ax.set_title(f'{country} — {label} Forecast (2025–2040)',
                 color=TEXT_COLOR, fontsize=13, fontweight='bold', pad=12)
    ax.set_xticks(years)
    ax.tick_params(axis='x', rotation=45)

    fig.tight_layout()
    prefix = f"forecast_{country.replace(' ', '_')}_{metric}"
    return _save_chart(fig, prefix)


def generate_multi_indicator_chart(df: pd.DataFrame, metrics: list, country: str) -> str:
    """Multi-line chart comparing several indicators over years."""
    valid_metrics = [m for m in metrics if m in df.columns]
    if not valid_metrics:
        return None

    fig, ax = _base_fig(figsize=(11, 5))
    years = df['Year'].astype(int).sort_values().unique()

    for i, metric in enumerate(valid_metrics):
        color = LINE_COLORS[i % len(LINE_COLORS)]
        data = df[['Year', metric]].dropna().sort_values('Year')
        if data.empty:
            continue
        label = METRIC_LABELS.get(metric, metric.replace('_', ' '))

        # Normalize to 0-100 so different-scale indicators are comparable
        vals = data[metric].astype(float)
        vmin, vmax = vals.min(), vals.max()
        if vmax - vmin > 0:
            norm_vals = (vals - vmin) / (vmax - vmin) * 100
        else:
            norm_vals = vals * 0 + 50

        ax.plot(data['Year'].astype(int), norm_vals,
                color=color, linewidth=2.2, marker='o',
                markersize=4.5, markerfacecolor='white',
                markeredgewidth=1.8, markeredgecolor=color,
                label=label, zorder=3)

    ax.set_xlabel('Year', color=SUBTEXT, fontsize=10)
    ax.set_ylabel('Normalized Value (0–100)', color=SUBTEXT, fontsize=10)
    ax.set_title(f'{country} — Multi-Indicator Comparison',
                 color=TEXT_COLOR, fontsize=13, fontweight='bold', pad=12)
    ax.legend(loc='upper left', frameon=True, framealpha=0.9,
              fontsize=8, edgecolor=GRID_COLOR)
    ax.set_xticks(years)
    ax.tick_params(axis='x', rotation=45)

    fig.tight_layout()
    metric_key = '_'.join(valid_metrics[:3])
    prefix = f"multi_{country.replace(' ', '_')}_{metric_key}"
    return _save_chart(fig, prefix)
