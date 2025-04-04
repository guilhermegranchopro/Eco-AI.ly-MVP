import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, timezone
from backend.api import fetch_power_breakdown_history, fetch_carbon_intensity_history

def render_time_series():
    st.markdown("---")
    st.subheader("Time Series Data")
    
    # Get the current time (UTC)
    now_dt = datetime.now(timezone.utc)
    
    # -----------------------------
    # Carbon Intensity Time Series
    # -----------------------------
    data_ci = fetch_carbon_intensity_history(zone="PT")
    if data_ci:
        historico_carbon = data_ci.get("history", [])
        if historico_carbon:
            df_ci = pd.DataFrame(historico_carbon)
            df_ci['datetime'] = pd.to_datetime(df_ci['datetime'])
            df_ci = df_ci.sort_values(by='datetime', ascending=True)
            if 'carbonIntensity' in df_ci.columns:
                # Select and rename columns
                df_ci = df_ci[['datetime', 'carbonIntensity']].copy()
                df_ci.rename(columns={'carbonIntensity': 'LCA'}, inplace=True)
                # Filter to the last 24 hours
                cutoff_ci = now_dt - timedelta(hours=24)
                df_ci_last24 = df_ci[df_ci['datetime'] >= cutoff_ci]
                if df_ci_last24.empty:
                    st.error("No carbon intensity data available for the last 24 hours.")
                else:
                    # Format time to include day/month and hour:minute
                    df_ci_last24['Time'] = df_ci_last24['datetime'].dt.strftime('%d/%m %H:%M')
                    # Create an interactive Altair line chart with zoom/pan selection
                    brush = alt.selection_interval(encodings=['x'])
                    base_chart = alt.Chart(df_ci_last24).mark_line(color='green').encode(
                        x=alt.X('Time:N', title='Time (Last 24 Hours)', axis=alt.Axis(labelAngle=-45)),
                        y=alt.Y('LCA:Q', title='Carbon Intensity (gCO₂/kWh)'),
                        tooltip=[alt.Tooltip('Time:N', title='Time'),
                                 alt.Tooltip('LCA:Q', title='Carbon Intensity (gCO₂/kWh)')]
                    ).properties(
                        title='Carbon Intensity Over the Last 24 Hours',
                        width=700,
                        height=400
                    ).add_selection(
                        brush
                    ).interactive()

                    # Overlay circle markers
                    points = base_chart.mark_circle(size=60, color='green').encode(
                        tooltip=[alt.Tooltip('Time:N', title='Time'),
                                 alt.Tooltip('LCA:Q', title='CI (gCO₂/kWh)')]
                    )
                    
                    chart_ci = alt.layer(base_chart, points).resolve_scale(x='shared')
                    st.altair_chart(chart_ci, use_container_width=True)
            else:
                st.error("API data does not contain 'carbonIntensity'.")
        else:
            st.error("No carbon intensity history data available.")
    else:
        st.error("Error fetching carbon intensity data.")
    
    # ------------------------------------
    # Renewable Percentage Time Series
    # ------------------------------------
    data_rp = fetch_power_breakdown_history(zone="PT")
    if data_rp:
        historico_rp = data_rp.get("history", [])
        if historico_rp:
            df_rp = pd.DataFrame(historico_rp)
            df_rp['datetime'] = pd.to_datetime(df_rp['datetime'])
            df_rp = df_rp.sort_values(by='datetime', ascending=True)
            if 'renewablePercentage' in df_rp.columns:
                df_rp = df_rp[['datetime', 'renewablePercentage']].copy()
                df_rp.rename(columns={'renewablePercentage': 'RP'}, inplace=True)
                cutoff_rp = now_dt - timedelta(hours=24)
                df_rp_last24 = df_rp[df_rp['datetime'] >= cutoff_rp]
                if df_rp_last24.empty:
                    st.error("No renewable percentage data available for the last 24 hours.")
                else:
                    df_rp_last24['Time'] = df_rp_last24['datetime'].dt.strftime('%d/%m %H:%M')
                    brush_rp = alt.selection_interval(encodings=['x'])
                    base_chart_rp = alt.Chart(df_rp_last24).mark_line(color='blue').encode(
                        x=alt.X('Time:N', title='Time (Last 24 Hours)', axis=alt.Axis(labelAngle=-45)),
                        y=alt.Y('RP:Q', title='Renewable Percentage (%)'),
                        tooltip=[alt.Tooltip('Time:N', title='Time'),
                                 alt.Tooltip('RP:Q', title='Renewable Percentage (%)')]
                    ).properties(
                        title='Renewable Percentage Over the Last 24 Hours',
                        width=700,
                        height=400
                    ).add_selection(
                        brush_rp
                    ).interactive()
                    
                    points_rp = base_chart_rp.mark_circle(size=60, color='blue').encode(
                        tooltip=[alt.Tooltip('Time:N', title='Time'),
                                 alt.Tooltip('RP:Q', title='RP (%)')]
                    )
                    
                    chart_rp = alt.layer(base_chart_rp, points_rp).resolve_scale(x='shared')
                    st.altair_chart(chart_rp, use_container_width=True)
            else:
                st.error("API data does not contain 'renewablePercentage'.")
        else:
            st.error("No renewable percentage history data available.")
    else:
        st.error("Error fetching renewable percentage data.")

if __name__ == "__main__":
    render_time_series()
    # Uncomment the line below to run the function directly
    # render_time_series()
