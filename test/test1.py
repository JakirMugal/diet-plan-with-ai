import streamlit as st
from groq import Groq
import os
from fpdf import FPDF
import base64
import pdfkit
import tempfile
from weasyprint import HTML

# Set your Groq API key

client = Groq(api_key=os.environ["GROQ_API_KEY"])

st.title("🎯 AI-Powered Diet Planner (Groq + LLaMA)")

# ---- Mandatory Fields First ----
st.header("📏 Body Metrics (Required)")
height = st.number_input("Height (in cm):", min_value=50.0, max_value=250.0, step=0.1)
weight = st.number_input("Weight (in kg):", min_value=10.0, max_value=300.0, step=0.1)

# ---- Optional Fields ----
st.header("⚙️ Additional Preferences (Optional)")
diet_type = st.radio("Diet Type:", ["", "Vegetarian", "Non-Vegetarian"], index=0)
do_workout = st.selectbox("Do you workout?", ["", "Yes", "No"])
workout_time = st.time_input("Workout Time (if any):") if do_workout == "Yes" else None
body_fat = st.slider("Body Fat Percentage (optional):", 1, 60) if st.checkbox("Add Body Fat %") else None
food_options = ["Eggs", "Chicken", "Tofu", "Broccoli", "Milk", "Oats", "Paneer", "Nuts", "Whey Protein"]
selected_foods = st.multiselect("Select foods to include:", food_options)
goal = st.selectbox("What's your goal?", ["", "Weight Loss", "Weight Gain"])
disease = st.text_area("Any diseases or medical conditions? (optional)")

# ---- Submit Button ----
if st.button("Generate Diet Plan"):
    if not height or not weight:
        st.error("Height and Weight are required to generate a diet plan.")
    else:
        with st.spinner("Creating personalized diet plan..."):

            # ----- Build Prompt Conditionally -----
            prompt_lines = [
                f"Create a personalized diet plan for someone with:",
                f"- Height: {height} cm",
                f"- Weight: {weight} kg"
            ]

            if diet_type:
                prompt_lines.append(f"- Diet Type: {diet_type}")
            if do_workout:
                prompt_lines.append(f"- Workout: {do_workout}")
            if workout_time:
                prompt_lines.append(f"- Workout Time: {workout_time.strftime('%H:%M')}")
            if body_fat:
                prompt_lines.append(f"- Body Fat %: {body_fat}")
            if selected_foods:
                prompt_lines.append(f"- Preferred Foods: {', '.join(selected_foods)}")
            if goal:
                prompt_lines.append(f"- Goal: {goal}")
            if disease:
                prompt_lines.append(f"- Medical Conditions: {disease.strip()}")

            prompt_lines.append("""
                                Please create the plan as I give the example below. This is just an example create according to input information.
                                Please create for whole week.
                                day (Mon, Tue ,..)
                                Time : 7:00 AM
                                Foods : 2 whole wheat bread, 1 tsp peanut butter
                                macros : x cal | y protien | s carbs | q fat
                                daily total macros : x cal | y protien | s carbs | q fat 
                                
                                Note : Output look likes Day Name : Total micors and below that a beatiful table with meals.
                                """)

            full_prompt = "\n".join(prompt_lines)

            # ----- Call Groq API -----
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.1,
                max_tokens=1024*8
            )

            reply = response.choices[0].message.content
            st.subheader("📝 Personalized Diet Plan")
            st.markdown(reply)
            # Convert markdown reply to basic HTML
            # HTML content based on your LLaMA reply
            html_content = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    h1, h2, h3 {{ color: #2c3e50; }}
                    ul {{ padding-left: 20px; }}
                </style>
            </head>
            <body>
                <h2>Personalized Diet Plan</h2>
                {reply.replace('\n', '<br>')}
            </body>
            </html>
            """

            # Save to temp PDF file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
                HTML(string=html_content).write_pdf(pdf_file.name)
                pdf_file.seek(0)
                pdf_bytes = pdf_file.read()

            # Download button
            st.download_button(
                label="📥 Download Diet Plan as PDF",
                data=pdf_bytes,
                file_name="diet_plan.pdf",
                mime="application/pdf"
            )
