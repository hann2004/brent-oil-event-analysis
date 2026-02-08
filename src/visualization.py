import matplotlib.pyplot as plt
import seaborn as sns


def setup_plotting_style() -> None:
    plt.style.use("seaborn-v0_8-darkgrid")
    sns.set_palette("husl")
    plt.rcParams["figure.figsize"] = (14, 6)
    plt.rcParams["font.size"] = 11


def plot_price_series(df, title="Brent Crude Oil Prices"):
    fig, ax = plt.subplots()
    ax.plot(df["Date"], df["Price"], linewidth=1.5, color="steelblue", alpha=0.85)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Price (USD/barrel)")
    ax.grid(True, alpha=0.3)
    return fig


def plot_log_returns(df, title="Daily Log Returns"):
    fig, ax = plt.subplots()
    ax.plot(df["Date"], df["Log_Returns"], linewidth=0.6, color="green", alpha=0.75)
    ax.axhline(0, color="black", linewidth=0.6, alpha=0.5)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Log Return")
    ax.grid(True, alpha=0.3)
    return fig


def plot_rolling_volatility(df, window=30, title="Rolling Volatility"):
    series = df["Log_Returns"].rolling(window=window).std()
    fig, ax = plt.subplots()
    ax.plot(df["Date"], series, linewidth=1.2, color="red", alpha=0.85)
    ax.set_title(f"{title} ({window}D)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Volatility")
    ax.grid(True, alpha=0.3)
    return fig
