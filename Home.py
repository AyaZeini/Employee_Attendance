import pandas as pd 
import streamlit as st
import numpy as np

import datetime
from datetime import datetime, timedelta

import sqlite3

import hydralit_components as hc
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import requests


import plotly.graph_objects as go
import plotly.express as px

import pickle

# Set page title and favicon
st.set_page_config(page_title="Attendance Management", page_icon="📶")

df= pd.read_csv('data/df.csv')
df1= pd.read_csv('data/all_data.csv')
df2 =pd.read_csv('data/tasks.csv')
df3 = pd.read_csv('data/absence.csv')


# Load the model from the file
with open('linearRegression.pkl', 'rb') as file:
    model = pickle.load(file)


# Display lottie animations
def load_lottieurl(url):

    # get the url
    r = requests.get(url)
    # if error 200 raised return Nothing
    if r.status_code !=200:
        return None
    return r.json()

lottie1 = load_lottieurl("https://lottie.host/5e9b6f14-5a00-4c0d-90a3-b8ac2c842179/lNJwFiZk7N.json")


 # Convert "Date" column to datetime format
df1['Date'] = pd.to_datetime(df1['Date'])
df1['Check-In Time'] = pd.to_datetime(df1['Check-In Time'])
df1['Check-Out Time'] = pd.to_datetime(df1['Check-Out Time'])


# Convert 'Status' column to boolean
df1['Status'] = df1['Status'] == 'Present'



# Page layout
st.title("Employee Attendance Application")


#with st.sidebar:
selected= option_menu(
    menu_title=None,
    options=['Manager','Employee'],
    icons=['person'],
    menu_icon="cast",
    default_index=0,
    orientation='horizontal',
    styles={
        "container": {"padding": "0!important"}
        #"nav-link": {"font-size": "18px", "text-align": "left", "margin": "0px", "--hover-color": "#eee", "color": "#000000"},
        #"nav-link-selected": {"background-color": "#ff9900", "color": "#ffffff"},
    }
)


usernameContainer = st.empty()

passwordContainer = st.empty()

infoeHeader = st.empty()


# CSS styling
st.markdown(
    """
    <style>
        .card {
            background-color: #4682A9;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Define a dictionary to store vacation requests (outside of sections)
vacation_requests = {}

# Function to submit vacation request from the employee section
def submit_vacation_request(employee_name, start_date, end_date, absence_type):
    # Store the vacation request in the shared dictionary
    vacation_requests[employee_name] = {
        "start_date": start_date,
        "end_date": end_date,
        "absence_type": absence_type,
        "status": "Pending"
    }


## EMPLOYEE SECTION

if selected=="Employee":
    # Define a function to check the login credentials
    def authenticate_user(username, password):
        return username == "RachelBrown" and password == "Rachel_1" # You can replace this with your own authentication logic

    # Define a function to display the login form and get the credentials
    def get_login_credentials():
        infoeHeader.write("Please login to access the section")
        username = usernameContainer.text_input("Username")
        password = passwordContainer.text_input("Password", type="password")
        return username, password

    # Define the main function for the Employees section
    def employees_section():
        # Get the login credentials from the user
        username, password = get_login_credentials()
        # Check the credentials
        if not authenticate_user(username, password):
            st.error("Incorrect username or password. Please try again.")
        else:
            st.success("Logged in successfully!")
            usernameContainer.empty()
            passwordContainer.empty()
            infoeHeader.empty()

            st.empty()

            # Navigation Bar Design
            menu_data = [
            {'label':"Home", 'icon': "bi bi-house"},
            {'label':"Task", 'icon': "bi bi-list-task"},
            {'label':"Schedule", 'icon': "bi bi-calendar-day"},
            ]

            # Set the Navigation Bar
            menu_id = hc.nav_bar(menu_definition = menu_data,
                                sticky_mode = 'sticky',
                                sticky_nav = False,
                                hide_streamlit_markers = False,
                                override_theme = {'txc_inactive': 'white',
                                                    'menu_background' : '#749BC2',
                                                    'txc_active':'#749BC2',
                                                    'option_active':'white'})

            employee_name = "Rachel Brown"


            if menu_id == "Home":


                rachel_data = df1[df1['Name'] == employee_name]

                # Calculate the average check-in and check-out times
                average_check_in = rachel_data['Check-In Time'].mean()
                average_check_out = rachel_data['Check-Out Time'].mean()

                average_check_in_formatted = average_check_in.strftime('%H:%M:%S')
                average_check_out_formatted = average_check_out.strftime('%H:%M:%S')
               

                # Calculate the average on-time percentage
                total_days = rachel_data['Date'].nunique()
                on_time_days = rachel_data[rachel_data['Early Check-In'] == False]['Date'].nunique()
                on_time_percentage = (on_time_days / total_days) * 100
                rounded_on_time_percentage = round(on_time_percentage, 2)

                # Calculate percentage of Absence
                Total_absence= rachel_data[rachel_data['Status'] == False]['Date'].nunique()
                absence_percentage = (Total_absence / total_days) * 100
                rounded_absence_percentage = round(absence_percentage, 2)


                # Display the calculated averages in cards
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    # Employee count card
                    with st.container():
                        st.markdown(f"<div class='card' style='color: white;'><h3 style='color: white;'>{average_check_in_formatted}</h3><p>Checked In</p></div>", unsafe_allow_html=True)

                with col2:
                    with st.container():
                        st.markdown(f"<div class='card' style='color: white;'><h3 style='color: white;'>{average_check_out_formatted}</h3><p>Checked Out</p></div>", unsafe_allow_html=True)

                with col3:
                    with st.container():
                        st.markdown(f"<div class='card' style='color: white;'><h3 style='color: white;'>{rounded_on_time_percentage}%</h3><p>On Time</p></div>", unsafe_allow_html=True)

                with col4:
                    with st.container():
                        st.markdown(f"<div class='card' style='color: white;'><h3 style='color: white;'>{rounded_absence_percentage}%</h3><p>Absence</p></div>", unsafe_allow_html=True)
                                        

                with st.expander('Attendance History'):
                    st.dataframe(rachel_data)


            if menu_id == 'Task':

                # Define a function to create a task card with progress and color customization
                def create_task_card(task_name, due_date, progress, progress_color):
                    st.markdown(
                        f"<div class='card' style='color: white; padding: 10px;'>"
                        f"<h3 style='color: white;'>{task_name}</h3>"
                        f"<p>Due Date: {due_date}</p>"
                        f"<progress value='{progress}' max='100' style='background-color: {progress_color};'></progress>"
                        f"<p>Progress: {progress}%</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                prog1, prog2, prog3 =st.columns(3)


                with prog1:
                    specific_task_name = "Product Use Analysis"
                    specific_task = df2[df2['Task Name'] == specific_task_name].iloc[0]

                    # Set the progress and color for the specific task
                    specific_progress = 75
                    specific_color = "#DBDFEA"  # You can customize the color as needed

                    # Print the specific task using the create_task_card function
                    with st.container():
                        create_task_card(
                            specific_task['Task Name'],
                            specific_task['Due Date'],
                            specific_progress,
                            specific_color
                        )

                with prog2:
                    specific_task_name = "Financial Data Analysis"
                    specific_task = df2[df2['Task Name'] == specific_task_name].iloc[0]

                    # Set the progress and color for the specific task
                    specific_progress = 60
                    specific_color = "#DBDFEA"  # You can customize the color as needed

                    # Print the specific task using the create_task_card function
                    with st.container():
                        create_task_card(
                            specific_task['Task Name'],
                            specific_task['Due Date'],
                            specific_progress,
                            specific_color
                        )

                with prog3:
                    specific_task_name = "Customer Segmentation"
                    specific_task = df2[df2['Task Name'] == specific_task_name].iloc[1]

                    # Set the progress and color for the specific task
                    specific_progress = 55
                    specific_color = "#DBDFEA"  # You can customize the color as needed

                    # Print the specific task using the create_task_card function
                    with st.container():
                        create_task_card(
                            specific_task['Task Name'],
                            specific_task['Due Date'],
                            specific_progress,
                            specific_color
                        )


                st.empty()

                st.markdown("<hr/>", unsafe_allow_html=True)  # Horizontal line 

                st.subheader('Tasks to do')
                st.dataframe(df2)

                st.empty()

                st.markdown("<hr/>", unsafe_allow_html=True)  # Horizontal line 

                st.subheader('Input Task')
                task_name = st.text_input('Task Name')
                due_date = st.date_input('Due Date')
                description = st.text_area('Description')


                if st.button('Add Task'):
                    # Get task data from the input fields
                    new_task = {'Task Name': task_name, 'Due Date': due_date, 'Description': description}

                    # Append the new task to the task_data DataFrame
                    task_data = df2.append(new_task, ignore_index=True)


                    if not task_data.empty:
                        st.table(task_data)
                    else:
                        st.write('No tasks added yet.')


            if menu_id == 'Schedule':

                # Function to display employee's absence data
                def display_employee_absence(employee_name):
                    employee_absence = df3[df3["Name"] == employee_name]
                    st.dataframe(employee_absence)

                # Display the absence data for employees
                st.subheader("Your Absence Data:")
                display_employee_absence(employee_name)

                st.markdown("<hr/>", unsafe_allow_html=True)  # Horizontal line 


                st.empty()


                st.subheader('Schedule Your Leave:')
                col1, col2 = st.columns(2)

                with col1: 
                    # Create date objects for January 1, 2023, and August 15, 2023
                    start_date = datetime(2023, 8, 15)
                    end_date = datetime(2023, 12, 31)

                    # Create separate date input widgets for the start and end dates
                    selected_start_date = st.date_input(
                        "Select Start Date",
                        start_date,
                        min_value=start_date,
                        max_value=end_date,
                        format="MM/DD/YYYY",
                    )

                    selected_end_date = st.date_input(
                        "Select End Date",
                        end_date,
                        min_value=start_date,
                        max_value=end_date,
                        format="MM/DD/YYYY",
                    )

                    # Define suggested absence types
                    suggested_absence_types = ["Vacation", "Sick Leave", "Personal Day", "Work From Home"]

                    # Create a dropdown for absence type with suggested options
                    absence_type = st.selectbox("Absence Type", suggested_absence_types)

                    # Calculate the remaining allowed absences based on the limit (e.g., 30 days)
                    allowed_absences_limit = 15

                    total_absence_days_for_year = df1[(df1['Name'] == employee_name) & (df1['Status'] == False)]['Date'].nunique()

                    remaining_absence_days = allowed_absences_limit - total_absence_days_for_year

                    selected_year = selected_start_date.year

                    # Button to schedule the absence

                    if st.button("Schedule Absence"):
                        if remaining_absence_days <= (selected_end_date - selected_start_date).days +1:
                            # Here's a simple example to display the scheduled absence information
                            st.error(f"Cannot schedule absence. Only {remaining_absence_days} days remaining for the year {selected_start_date.year}.")

                        else:
                            remaining_absence_days -= (selected_end_date - selected_start_date).days +1

                            submit_vacation_request(employee_name, start_date, end_date, absence_type)

                            st.success(f"Scheduled Absence: Date - {selected_start_date.strftime('%m-%d-%Y')} to {selected_end_date.strftime('%m-%d-%Y')}, Type - {absence_type}, Remaining Absence for {employee_name} - {remaining_absence_days}")                      
                           

                with col2: 
                    # Check if the selected absence type is "Sick Leave"
                    if absence_type == "Sick Leave":
                        uploaded_sick_note = st.file_uploader("Upload Sick Note (PDF or Image)")

                        if not uploaded_sick_note:
                            st.warning("Please upload a sick note for Sick Leave.")



    employees_section()



## MANAGER

if selected=="Manager":

    # Define a function to check the login credentials
    def authenticate_user(username, password):
        return username == "Data" and password == "Manager123" # You can replace this with your own authentication logic

    # Define a function to display the login form and get the credentials
    def get_login_credentials():
        infoeHeader.write("Please login to access the section")
        username = usernameContainer.text_input("Username")
        password = passwordContainer.text_input("Password", type="password")
        return username, password

    # Define the main function for the Employees section
    def manager_section():
        # Get the login credentials from the user
        username, password = get_login_credentials()
        # Check the credentials
        if not authenticate_user(username, password):
            st.error("Incorrect username or password. Please try again.")
        else:
            st.success("Logged in successfully!")
            usernameContainer.empty()
            passwordContainer.empty()
            infoeHeader.empty()

            st.empty()

            # Navigation Bar Design
            menu_data = [
            {'label':"Overview", 'icon': "bi bi-house"},
            {'label':"Absence", 'icon': "bi bi-calendar-day"},
            {'label':"Employee Productivity", 'icon': "bi bi-person-lines-fill"},
            ]

            # Set the Navigation Bar
            menu_id = hc.nav_bar(menu_definition = menu_data,
                                sticky_mode = 'sticky',
                                sticky_nav = False,
                                hide_streamlit_markers = False,
                                override_theme = {'txc_inactive': 'white',
                                                    'menu_background' : '#749BC2',
                                                    'txc_active':'#749BC2',
                                                    'option_active':'white'})

            if menu_id == "Overview":

                # Calculate the number of employees in the department
                total_employees = df1['Name'].nunique()

                # Calculate the number of employees on time
                on_time_employees = df1[df1['Check-In Time'] == df1['Schedule Starting Hour']]['Name'].nunique()
                percentage_on_time_employees = ( on_time_employees / total_employees) * 100

                # Calculate the percentage of on-time employees
                total_employees = df1['Name'].nunique()

                # Calculate the average number of days attended
                average_days_attended = df1.groupby('Name')['Status'].count().mean()

                # Calculate the average check-in and check-out times
                average_check_in_m = df1['Check-In Time'].mean()
                average_check_out_m = df1['Check-Out Time'].mean()

                average_check_in_formatted_m = average_check_in_m.strftime('%H:%M:%S')
                average_check_out_formatted_m = average_check_out_m.strftime('%H:%M:%S')


                card1, card2, card3, card4 = st.columns(4)

                with card1:
                    # Employee count card
                    with st.container():
                        st.markdown(f"<div class='card' style='color: white;'><h3 style='color: white;'>{total_employees}</h3><p>Total Employees</p></div>", unsafe_allow_html=True)

                with card2:
                    # Average days attended card
                    with st.container():
                        st.markdown(f"<div class='card' style='color: white;'><h3 style='color: white;'>{percentage_on_time_employees}%</h3><p>On Time</p></div>", unsafe_allow_html=True)

                with card3:
                    with st.container(): 
                        st.markdown(f"<div class='card' style='color: white;'><h3 style='color: white;'>{average_check_in_formatted_m}</h3><p>Checked In</p></div>", unsafe_allow_html=True)

                with card4:
                    with st.container(): 
                        st.markdown(f"<div class='card' style='color: white;'><h3 style='color: white;'>{average_check_out_formatted_m}</h3><p>Checked Out</p></div>", unsafe_allow_html=True)



                p1, p2 = st.columns(2, gap="large")

                with p1:

                    # Create a date input widget
                    d = st.date_input("Choose a date", datetime(2023, 1, 1))

                with p2:

                    # Create a widget to select an employee
                    all_selected_employee = 'All employees'
                    employee_options = df1['Name'].unique().tolist()
                    employee_options.insert(0, all_selected_employee)
                    selected_employee = st.selectbox('Select an employee', employee_options)

                    # Filter the 'df1' DataFrame for the selected date(s) and employee
                    if selected_employee == all_selected_employee:
                        filtered_data = df1[df1['Date'] == d.strftime('%d/%m/%Y')]
                    else:
                        filtered_data = df1[(df1['Date'] == d.strftime('%d/%m/%Y')) & (df1['Name'] == selected_employee)]

                # with p1:


                # Select the desired columns
                selected_columns = filtered_data[['Name', 'ID', 'Age', 'Status']]

                # Convert 'Check-In Time' and 'Check-Out Time' to datetime objects
                filtered_data['Check-In Time'] = pd.to_datetime(filtered_data['Check-In Time']).dt.strftime('%H:%M:%S')
                filtered_data['Check-Out Time'] = pd.to_datetime(filtered_data['Check-Out Time']).dt.strftime('%H:%M:%S')

                # Add 'Check-In Time' and 'Check-Out Time' to selected_columns
                selected_columns['Check-In Time'] = filtered_data['Check-In Time']
                selected_columns['Check-Out Time'] = filtered_data['Check-Out Time']

                selected_columns['Late Check-In'] = filtered_data['Late Check-In']

                st.write('Attendance Overview')
                st.data_editor(
                    selected_columns,
                    column_config={
                        "Status": st.column_config.CheckboxColumn(
                            "Status",
                            help="Employee is Present or Absent ?",
                            default= False,
                        )
                    },
                    disabled=["Status", "Late Check-In"],
                    hide_index=True,

                )

            if menu_id == "Absence":

                all_selected_employee = 'All employees'
                employee_options = df1['Name'].unique().tolist()
                employee_options.insert(0, all_selected_employee)
                selected_employee = st.selectbox('Select an employee', employee_options)

                # Filter the 'df3' DataFrame for the selected date(s) and employee
                if selected_employee == all_selected_employee:
                    filtered_data2 = df1.copy()
                else:
                    filtered_data2 = df1[df1['Name'] == selected_employee]

                # Calculate the number of absences for each employee
                absence_counts = filtered_data2[filtered_data2['Status'] == False].groupby('Name').size().reset_index(name='Absence Count')

                st.write("Number of Absences")
                st.dataframe(absence_counts)

                st.markdown("<hr/>", unsafe_allow_html=True)  # Horizontal line 

                st.empty()

                st.write("Vacation Approval")
                
                if st.button("Check Vacation Requests"):
                    # Display a list of pending vacation requests
                    pending_requests = {k: v for k, v in vacation_requests.items() if v["status"] == "Pending"}
                    
                    if  pending_requests:
                        st.write("Pending Vacation Requests:")
                        for employee, request in pending_requests.items():
                            st.write(f"Employee: {employee}")
                            st.write(f"Start Date: {request['start_date']}")
                            st.write(f"End Date: {request['end_date']}")
                            st.write(f"Absence Type: {request['absence_type']}")
                            
                            # Add buttons for the manager to approve or deny the request
                            if st.button(f"Approve {employee}'s Request"):
                                vacation_requests[employee]["status"] = "Approved"
                                st.success(f"Approved vacation request for {employee}.")
                            
                            if st.button(f"Deny {employee}'s Request"):
                                vacation_requests[employee]["status"] = "Denied"
                                st.warning(f"Denied vacation request for {employee}.")
                    else:
                        st.info("No pending vacation requests.")


            if menu_id == "Employee Productivity":
                # Streamlit app title
                st.title("Employee Productivity Prediction")

                # Input form for user
                st.sidebar.header("Input Features")


                # Get unique employee IDs
                unique_ids = df['ID'].unique()

                day_name_to_number = {
                    "Monday": 1,
                    "Tuesday": 2,
                    "Wednesday": 3,
                    "Thursday": 4,
                    "Friday": 5,
                    "Saturday": 6,
                    "Sunday": 7
                }

                selected_id = st.sidebar.selectbox("Select Employee ID", unique_ids)     # Sidebar widget for selecting an employee ID
                selected_day_name = st.sidebar.selectbox("Select Day of Week", list(day_name_to_number.keys()))  # Sidebar widget for selecting the day of the week
                selected_day_number = day_name_to_number[selected_day_name]  # Get the corresponding number
                targeted_productivity = st.sidebar.number_input("targeted_productivity", min_value=0.0, max_value=1.0, step=0.01)
                smv = st.sidebar.number_input("smv", min_value=0.0)
                wip = st.sidebar.number_input("wip", min_value=0)
                over_time = st.sidebar.number_input("over_time", min_value=0)
                incentive = st.sidebar.number_input("incentive", min_value=0)
                idle_time = st.sidebar.number_input("idle_time", min_value=0)

                # Prepare user input data as a DataFrame
                user_input = pd.DataFrame({
                    'ID': [selected_id],
                    'Targeted Productivity': [targeted_productivity],
                    'Standard Minute Value': [smv],
                    'Work In Progress': [wip],
                    'Overtime': [over_time],
                    'Incentive': [incentive],
                    'Productivity Interruption': [idle_time],
                    'Day of Week': [selected_day_number]
                })

                pred1, pred2 = st.columns(2)

                with pred1:
                    # When the user clicks the prediction button
                    if st.button("Predict"):
                        # Use the loaded model to make predictions
                        prediction = model.predict(user_input)
                        # Round the prediction to 2 decimal places
                        rounded_prediction = round(prediction[0], 3)
                        # Check if predicted productivity is greater than or equal to the target productivity
                        if rounded_prediction >= user_input['Targeted Productivity'].values[0]:
                            # If so, give a positive message
                            message = " Great news! 🌟 You're expected to exceed your target productivity at:"
                        else:
                            # If not, give an encouraging message
                            message = "🌟 Keep up the good work! Your expected productivity is at:"

                        # Add some excitement!
                        st.write(f"{message} 🌟 {rounded_prediction:.3f} 🌟")

                        # st.write(f"Based on the provided inputs, the estimated productivity is: {rounded_prediction}")





                with pred2:
                    # Display customer churn animation
                    st_lottie(lottie1, key="employee")








    manager_section()















