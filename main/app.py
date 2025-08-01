import streamlit as st
from groq import Groq
import os
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime, time
api_key = st.secrets["GROQ_API_KEY"]

# Debug: show if key is loaded
if not api_key:
    st.error("GROQ_API_KEY not found. Check your .env file path.")
else:
    st.success("API key loaded successfully!")


client = Groq(api_key=api_key)

st.title("🎯 AI-Powered Diet Planner By Jakir")

# Generate AM/PM time slots (every 30 minutes)
def generate_time_slots(interval_minutes=30):
    times = []
    for hour in range(24):
        for minute in range(0, 60, interval_minutes):
            t = time(hour, minute)
            times.append(t.strftime('%I:%M %p'))
    return times

time_options = generate_time_slots()
# ---- Required Body Metrics ----
st.header("📏 Body Metrics (Required)")
height = st.number_input("Height (in cm):", min_value=50.0, max_value=250.0, step=0.1)
weight = st.number_input("Weight (in kg):", min_value=10.0, max_value=300.0, step=0.1)

# ---- Optional Fields ----
st.header("⚙️ Additional Preferences (Optional)")
diet_type = st.multiselect("Diet Type(s):", ["Vegetarian", "Eggitarian", "Non-Vegetarian"])
do_workout = st.selectbox("Do you workout?", ["", "Yes", "No"])

time_options = [
    "4:00 AM", "5:00 AM", "6:00 AM", "7:00 AM", "8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM",
    "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM", "6:00 PM", "7:00 PM", "8:00 PM", "9:00 PM"
]

workout_start_time = workout_end_time = workout_days = None
if do_workout == "Yes":
    workout_start_time = st.selectbox("Workout Start Time (AM/PM):", time_options)
    workout_end_time = st.selectbox("Workout End Time (AM/PM):", time_options)
    workout_days = st.slider("How many days a week do you workout?", 1, 7)

body_fat = st.slider("Body Fat Percentage (optional):", 1, 60) if st.checkbox("Add Body Fat %") else None

goal = st.multiselect(
    "What's your primary fitness goal?", 
    [
        "Fat Loss", 
        "Muscle Building", 
        "Recomposition (Lose fat + build muscle)", 
        "Improve Endurance", 
        "Improve General Health", 
        "Sports Performance", 
        "Other"
    ]
)

disease = st.text_area("Any diseases or medical conditions? (optional)")

# ---- Supplements Section ----
st.header("💊 Supplements (Optional)")
supplements_list = ["Multivitamin", "Omega-3", "Vitamin D", "Protein Powder", "Creatine", "Calcium", "Magnesium"]
selected_supplements = st.multiselect("Select supplements you take:", supplements_list)

# Timings for supplements using dropdown
supplement_timings = {}
for supp in selected_supplements:
    supplement_timings[supp] = st.selectbox(f"Timing for {supp}:", time_options, key=f"time_{supp}")

# ---- Chat Box for Custom Preferences ----
st.header("💬 Personal Preferences (Optional)")
custom_preferences = st.text_area("Tell us more about your preferences, allergies, or lifestyle:")

# ---- Indian Cuisine Preferences Section ----
st.header("🍛 Indian Cuisine Preferences (Optional)")
indian_cuisines = [
    "North Indian", "South Indian", "Gujarati", "Bengali", 
    "Rajasthani", "Maharashtrian", "Kerala"
]
selected_indian_cuisines = st.multiselect("Select your preferred Indian cuisines:", indian_cuisines)

# ---- Meal Preferences Section ----
st.header("🍽️ Meal Preferences")
num_meals = st.selectbox("How many meals do you want in a day?", [3, 4, 5, 6])
create_specific_meal_times = st.checkbox("Do you want to specify meal timings?")

meal_timings = {}
if create_specific_meal_times:
    st.subheader("🕒 Set Meal Timings")
    for i in range(1, num_meals + 1):
        meal_timings[f"Meal {i}"] = st.selectbox(f"Time for Meal {i}:", time_options, key=f"meal_time_{i}")

# ---- Submit Button ----
if st.button("Generate Diet Plan"):
    if not height or not weight:
        st.error("Height and Weight are required to generate a diet plan.")
    else:
        with st.spinner("Creating personalized diet plan..."):

            prompt_lines = [
                f"Create a personalized diet plan for someone with:",
                f"- Height: {height} cm",
                f"- Weight: {weight} kg"
            ]

            if diet_type:
                prompt_lines.append(f"- Diet Type(s): {', '.join(diet_type)}")
            if do_workout == "Yes":
                prompt_lines.append(f"- Workout: Yes")
                if workout_start_time and workout_end_time:
                    prompt_lines.append(f"- Workout Time: From {workout_start_time} to {workout_end_time}")
                if workout_days:
                    prompt_lines.append(f"- Workout Frequency: {workout_days} days per week")
            elif do_workout == "No":
                prompt_lines.append(f"- Workout: No")
            if body_fat:
                prompt_lines.append(f"- Body Fat %: {body_fat}")
            if goal:
                prompt_lines.append(f"- Goal(s): {', '.join(goal)}")
            if disease:
                prompt_lines.append(f"- Medical Conditions: {disease.strip()}")
            if selected_supplements:
                prompt_lines.append("- Supplements taken:")
                for supp in selected_supplements:
                    prompt_lines.append(f"  - {supp} at {supplement_timings[supp]}")
            if custom_preferences:
                prompt_lines.append(f"- User Preferences: {custom_preferences.strip()}")
            if selected_indian_cuisines:
                prompt_lines.append(f"- Preferred Indian Cuisines: {', '.join(selected_indian_cuisines)}")

            # Meal details
            prompt_lines.append(f"- Number of meals: {num_meals}")
            if create_specific_meal_times:
                prompt_lines.append("- Meal Timings:")
                for meal, timing in meal_timings.items():
                    prompt_lines.append(f"  - {meal} at {timing}")

            # Output the constructed prompt (or send to API)
            st.success("Prompt generated successfully:")
            st.text("\n".join(prompt_lines))


            prompt = """
Create a 7-day Indian meal plan in clean HTML format using the exact structure and styling below.

📌 HTML Formatting Rules:
- Day name (e.g., "Monday") should be in <h2> tags to act as the main heading (large and bold).
- Each meal should be in a <h3> tag (e.g., "Meal 1: 8:00 AM").
- Use <strong> tags only for the labels "Food:" and "Macros:".
- The actual food items and macro values should be plain text.
- Use <br> to separate lines and add <br><br> to leave space between meals.
- At the end of each day, include:
  📊 Daily Total<br>
  ✅ [macro totals]<br>
  Note: [short summary]<br><br>

⛔ Do not use example food items from the prompt. The model should choose all foods based on balanced nutrition (high protein, moderate carbs, healthy fats).

✅ Structure should be repeated exactly for all 7 days (Monday to Sunday).
✅ Only return valid, clean HTML. Do not include markdown, plain text, or code blocks.

---

Example for one day (structure only — actual content should be generated by the model):

<h2>Monday</h2>

<h3>Meal 1: 8:00 AM</h3>
<strong>Food:</strong> [model selects food here]<br>
<strong>Macros:</strong> [calories] kcal | [protein]g P | [carbs]g C | [fat]g F<br><br>

<h3>Meal 2: 11:00 AM</h3>
<strong>Food:</strong> [model selects food here]<br>
<strong>Macros:</strong> ...<br><br>

<h3>Meal 3: 2:00 PM</h3>
<strong>Food:</strong> ...<br>
<strong>Macros:</strong> ...<br><br>

<h3>Meal 4: 6:00 PM</h3>
<strong>Food:</strong> ...<br>
<strong>Macros:</strong> ...<br><br>

📊 Daily Total<br>
✅ [calories] kcal | [total protein]g Protein | [total carbs]g Carbs | [total fat]g Fat<br>
Note: [brief summary about the day’s nutrition]<br><br>

---

Repeat for Tuesday to Sunday using the same structure.
Note : Please be carefull with the following points.
1. If you see supliments then use the supliment with with in the meal.
2. Please create Indian diet plan.
3. If there is something written in the preferences be carefull with those and create according to the preferences.
4. Be carfull about the timings as workout time and supliment time should be considered very seriouslly.
"""

            prompt_lines.append(prompt)

            full_prompt = "\n".join(prompt_lines)

            # ----- Call Groq API -----
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.8,
                max_tokens=1024*8
            )

            reply = response.choices[0].message.content
            st.subheader("📝 Personalized Diet Plan")
            print(reply)
            st.markdown(reply, unsafe_allow_html=True)
            # Create a BytesIO buffer
            pdf_buffer = BytesIO()
            pisa.CreatePDF(reply, dest=pdf_buffer)
            pdf_buffer.seek(0)
            # Use Streamlit download button with bytes data
            st.download_button(
                label="Download Meal Plan PDF",
                data=pdf_buffer,
                file_name="meal_plan.pdf",
                mime="application/pdf"
            )