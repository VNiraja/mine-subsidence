import streamlit as st
import requests
import pandas as pd


API_URL = "http://127.0.0.1:8000/predict"


st.set_page_config(
    page_title="Mine Subsidence AI",
    page_icon="⛏️",
    layout="wide"
)


st.title("⛏️ Mine Subsidence Monitoring & Early Warning System")

st.write(
    "AI-powered monitoring using InSAR, seismic and IoT sensor data."
)


st.divider()


# -----------------------------
# SENSOR INPUT
# -----------------------------

st.subheader("Live Sensor Data")


col1, col2, col3, col4 = st.columns(4)


with col1:

    tilt = st.number_input(
        "Tilt (degrees)",
        min_value=-90.0,
        max_value=90.0,
        value=0.0
    )


with col2:

    displacement = st.number_input(
        "Displacement (mm)",
        min_value=0.0,
        value=0.0
    )


with col3:

    crack_width = st.number_input(
        "Crack Width (mm)",
        min_value=0.0,
        value=0.0
    )


with col4:

    strain = st.number_input(
        "Strain (µε)",
        min_value=0.0,
        value=0.0
    )


st.divider()


# -----------------------------
# PREDICTION
# -----------------------------

if st.button(
    "🔍 Predict Risk",
    use_container_width=True
):

    payload = {

        "tilt": tilt,

        "displacement": displacement,

        "crack_width": crack_width,

        "strain": strain
    }

    try:

        response = requests.post(
            API_URL,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:

            result = response.json()

            risk = result["risk_level"]

            confidence = result.get(
                "confidence"
            )

            action = result["action_signal"]


            st.subheader(
                "Prediction"
            )


            if str(risk).upper() == "CRITICAL":

                st.error(
                    "🚨 CRITICAL RISK"
                )

            elif str(risk).upper() == "HIGH":

                st.error(
                    "🔴 HIGH RISK"
                )

            elif str(risk).upper() in [
                "MODERATE",
                "MEDIUM",
                "WARNING"
            ]:

                st.warning(
                    "🟡 MODERATE / WARNING"
                )

            else:

                st.success(
                    "🟢 LOW / SAFE"
                )


            col1, col2 = st.columns(2)


            with col1:

                st.metric(
                    "Risk Level",
                    str(risk)
                )


            with col2:

                if confidence is not None:

                    st.metric(
                        "Confidence",
                        f"{confidence * 100:.2f}%"
                    )


            st.info(
                f"Recommended action signal: {action}"
            )


        else:

            st.error(
                f"API Error: {response.text}"
            )


    except requests.exceptions.RequestException:

        st.error(
            "Could not connect to FastAPI. "
            "Start backend first."
        )


st.divider()


# -----------------------------
# CURRENT SENSOR VALUES
# -----------------------------

st.subheader("Current Sensor Values")


sensor_df = pd.DataFrame({

    "Parameter": [
        "Tilt",
        "Displacement",
        "Crack Width",
        "Strain"
    ],

    "Value": [
        tilt,
        displacement,
        crack_width,
        strain
    ]

})


st.dataframe(
    sensor_df,
    use_container_width=True
)