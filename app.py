import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask_mail import Mail, Message

from flask import Flask, redirect, render_template, request, session, url_for, json
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
# Add credentials to the account. Details removed for security.
creds = ServiceAccountCredentials.from_json_keyfile_name('', scope)
# Authorize the clientsheet 
client = gspread.authorize(creds)

# Configure server parameters. Details removed for security.
app.config['MAIL_SERVER']=''
app.config['MAIL_PORT'] = 
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_DEFAULT_SENDER'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
# Create instance of mail class
mail = Mail(app)


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
    

@app.route("/")
def index():
    # NTURO Homepage    
    return render_template("index.html")


@app.route("/about")
def about():
    # NTURO About Page
    return render_template("about.html")


@app.route("/categories")
def categories():
    # NTURO Race Categories Page
    return render_template("categories.html")


@app.route("/overview")
def overview():
    # NTURO Overview Page
    return render_template("overview.html")


@app.route("/information")
def information():
    # NTURO Race Information Page
    return render_template("info.html")


@app.route("/submission", methods=["GET", "POST"])
def submission():
    # NTURO Submissions Page
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get Race Category & Gender
        race_cat = request.form.get("race_cat")
        gender = request.form.get("gender")

        # Get appropriate Google Forms Link
        if race_cat == "indiv_10km":
            if gender == "male":
                submission_url = "https://forms.gle/BLgAcXh2DN8DmGey5"
            else:
                submission_url = "https://forms.gle/KM2WoM9iXwxK7SRE7"
        elif race_cat == "indiv_42km":
            if gender == "male":
                submission_url = "https://forms.gle/gttDpNnfwdQvPouc9"
            else:
                submission_url = "https://forms.gle/WpVazRjW62kXABzg8"
        elif race_cat == "indiv_75km":
            if gender == "male":
                submission_url = "https://forms.gle/ZwweMesFPNsMVfTM7"
            else:
                submission_url = "https://forms.gle/DcAkDgWaLYgH9qWRA"
        elif race_cat == "indiv_100km":
            if gender == "male":
                submission_url = "https://forms.gle/g3MRi1VU5KwYj6hh9"
            else:
                submission_url = "https://forms.gle/4AVfxYtQerESTGAa7"
        elif race_cat == "team_42km":
            submission_url = "https://forms.gle/KSjLstKRNJ5d4CRa9"
        elif race_cat == "team_200km":      
            submission_url = "https://forms.gle/vSWPvbchp8CMesni6"
        elif race_cat == "challenge1":
            submission_url = "https://forms.gle/7ixFTfKpUf7wAVBr6"
        elif race_cat == "challenge2":
            submission_url = "https://forms.gle/B5qSFxQhwpTcpWLK6"
        else:
            submission_url = "https://forms.gle/LBgnVbw6u9SHrEmA7"
        # Redirect to the appropriate Submission Google Form
        return redirect(submission_url)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("submission.html")


@app.route("/leaderboards/<category>")
def leaderboards(category):
    # NTURO Leaderboards Page

    # Swim Challenge Leaderboard
    if category == "swim_leaderboard":
        challenge_sheet = client.open("Challenges Leaderboards")
        challenge_sheet_list = challenge_sheet.worksheets()
        swim_sheet_instance = challenge_sheet_list[0]
        swim_data = swim_sheet_instance.batch_get(['A1:C200'])
        swim_data = swim_data[0]
        swim_headers = swim_data.pop(0)
        swim_df = pd.DataFrame(swim_data, columns=swim_headers)
        swim = swim_df.values.tolist()
        return render_template("swim_leaderboard.html", swim=swim)

    # Creativity Challenge Leaderboard
    elif category == "creativity_leaderboard":
        return render_template("creativity_leaderboard.html")

    # Elevation Challenge Leaderboard
    elif category == "elevation_leaderboard":
        category = "Side Quest 3 Elevation"
        challenge_sheet = client.open("Challenges Leaderboards")
        challenge_sheet_list = challenge_sheet.worksheets()
        elevation_sheet_instance = challenge_sheet_list[2]
        elevation_data = elevation_sheet_instance.batch_get(['A1:B200'])
        elevation_data = elevation_data[0]
        elevation_headers = elevation_data.pop(0)
        elevation_df = pd.DataFrame(elevation_data, columns=elevation_headers)
        elevation_df['Elevation Gain (M)'] = pd.to_numeric(elevation_df['Elevation Gain (M)'])
        elevation_df = elevation_df.sort_values(by="Elevation Gain (M)", ascending=False)
        elevation = elevation_df.values.tolist()
        rank = 0
        space = 0
        for index in range(len(elevation)):
            if index == 0:
                rank += 1
                elevation[index].insert(0, rank)
            else:
                if elevation[index][1] != elevation[index - 1][2]: 
                    rank += 1 + space
                    space = 0
                else:
                    space += 1
                elevation[index].insert(0, rank)
        return render_template("elevation_leaderboard.html", elevation=elevation)

    # Individual Male 10KM Leaderboard    
    elif category == "m10_leaderboard":
        category = "Individual Male 10KM"
        indiv_sheet = client.open("Individual Leaderboards")
        indiv_sheet_list = indiv_sheet.worksheets()
        indiv_sheet = client.open("Individual Leaderboards")
        indiv_sheet_list = indiv_sheet.worksheets()
        m10_sheet_instance = indiv_sheet_list[0]
        m10_data = m10_sheet_instance.batch_get(['A1:B100'])
        m10_data = m10_data[0]
        m10_headers = m10_data.pop(0)
        m10_df = pd.DataFrame(m10_data, columns=m10_headers)
        m10_df['Total Distance (KM)'] = pd.to_numeric(m10_df['Total Distance (KM)'])
        m10_df = m10_df.sort_values(by="Total Distance (KM)", ascending=False)
        m10 = m10_df.values.tolist()
        rank = 0
        space = 0
        for index in range(len(m10)):
            if index == 0:
                rank += 1 
                m10[index].insert(0, rank)
            else:
                if m10[index][1] != m10[index - 1][2]: 
                    rank += 1 + space
                    space = 0
                else:
                    space += 1
                m10[index].insert(0, rank)
        values = m10

    # Individual Male 42KM Leaderboard
    elif category == "m42_leaderboard":
        category = "Individual Male 42KM"
        indiv_sheet = client.open("Individual Leaderboards")
        indiv_sheet_list = indiv_sheet.worksheets()
        m42_sheet_instance = indiv_sheet_list[1]
        m42_data = m42_sheet_instance.batch_get(['A1:B100'])
        m42_data = m42_data[0]
        m42_headers = m42_data.pop(0)
        m42_df = pd.DataFrame(m42_data, columns=m42_headers)
        m42_df['Total Distance (KM)'] = pd.to_numeric(m42_df['Total Distance (KM)'])
        m42_df = m42_df.sort_values(by="Total Distance (KM)", ascending=False)
        m42 = m42_df.values.tolist()
        rank = 0
        space = 0
        for index in range(len(m42)):
            if index == 0:
                rank += 1 
                m42[index].insert(0, rank)
            else:
                if m42[index][1] != m42[index - 1][2]: 
                    rank += 1 + space
                    space = 0
                else:
                    space += 1
                m42[index].insert(0, rank)
        values = m42

    # Individual Male 75KM Leaderboard
    elif category == "m75_leaderboard":
        category = "Individual Male 75KM"
        indiv_sheet = client.open("Individual Leaderboards")
        indiv_sheet_list = indiv_sheet.worksheets()
        m75_sheet_instance = indiv_sheet_list[2]
        m75_data = m75_sheet_instance.batch_get(['A1:B100'])
        m75_data = m75_data[0]
        m75_headers = m75_data.pop(0)
        m75_df = pd.DataFrame(m75_data, columns=m75_headers)
        m75_df['Total Distance (KM)'] = pd.to_numeric(m75_df['Total Distance (KM)'])
        m75_df = m75_df.sort_values(by="Total Distance (KM)", ascending=False)
        m75 = m75_df.values.tolist()
        rank = 0
        space = 0
        for index in range(len(m75)):
            if index == 0:
                rank += 1 
                m75[index].insert(0, rank)
            else:
                if m75[index][1] != m75[index - 1][2]: 
                    rank += 1 + space
                    space = 0
                else:
                    space += 1
                m75[index].insert(0, rank)
        values = m75

    # Individual Male 100KM Leaderboard
    elif category == "m100_leaderboard":
        category = "Individual Male 100KM"
        indiv_sheet = client.open("Individual Leaderboards")
        indiv_sheet_list = indiv_sheet.worksheets()
        m100_sheet_instance = indiv_sheet_list[3]
        m100_data = m100_sheet_instance.batch_get(['A1:B100'])
        m100_data = m100_data[0]
        m100_headers = m100_data.pop(0)
        m100_df = pd.DataFrame(m100_data, columns=m100_headers)
        m100_df['Total Distance (KM)'] = pd.to_numeric(m100_df['Total Distance (KM)'])
        m100_df = m100_df.sort_values(by="Total Distance (KM)", ascending=False)
        m100 = m100_df.values.tolist()
        rank = 0
        space = 0
        for index in range(len(m100)):
            if index == 0:
                rank += 1 
                m100[index].insert(0, rank)
            else:
                if m100[index][1] != m100[index - 1][2]: 
                    rank += 1 + space
                    space = 0
                else:
                    space += 1
                m100[index].insert(0, rank)
        values = m100

    # Individual Female 10KM Leaderboard
    elif category == "f10_leaderboard":
        category = "Individual Female 10KM"
        indiv_sheet = client.open("Individual Leaderboards")
        indiv_sheet_list = indiv_sheet.worksheets()
        f10_sheet_instance = indiv_sheet_list[4]
        f10_data = f10_sheet_instance.batch_get(['A1:B100'])
        f10_data = f10_data[0]
        f10_headers = f10_data.pop(0)
        f10_df = pd.DataFrame(f10_data, columns=f10_headers)
        f10_df['Total Distance (KM)'] = pd.to_numeric(f10_df['Total Distance (KM)'])
        f10_df = f10_df.sort_values(by="Total Distance (KM)", ascending=False)
        f10 = f10_df.values.tolist()
        rank = 0
        space = 0
        for index in range(len(f10)):
            if index == 0:
                rank += 1
                f10[index].insert(0, rank)
            else:
                if f10[index][1] != f10[index - 1][2]: 
                    rank += 1 + space
                    space = 0
                else:
                    space += 1
                f10[index].insert(0, rank)
        values = f10

    # Individual Female 42KM Leaderboard
    elif category == "f42_leaderboard":
        category = "Individual Female 42KM"
        indiv_sheet = client.open("Individual Leaderboards")
        indiv_sheet_list = indiv_sheet.worksheets()
        f42_sheet_instance = indiv_sheet_list[5]
        f42_data = f42_sheet_instance.batch_get(['A1:B100'])
        f42_data = f42_data[0]
        f42_headers = f42_data.pop(0)
        f42_df = pd.DataFrame(f42_data, columns=f42_headers)
        f42_df['Total Distance (KM)'] = pd.to_numeric(f42_df['Total Distance (KM)'])
        f42_df = f42_df.sort_values(by="Total Distance (KM)", ascending=False)
        f42 = f42_df.values.tolist()
        rank = 0
        space = 0
        for index in range(len(f42)):
            if index == 0:
                rank += 1
                f42[index].insert(0, rank)
            else:
                if f42[index][1] != f42[index - 1][2]: 
                    rank += 1 + space
                    space = 0
                else:
                    space += 1
                f42[index].insert(0, rank)
        values = f42

    # Individual Female 75KM Leaderboard
    elif category == "f75_leaderboard":
        category = "Individual Female 75KM"
        indiv_sheet = client.open("Individual Leaderboards")
        indiv_sheet_list = indiv_sheet.worksheets()
        f75_sheet_instance = indiv_sheet_list[6]
        f75_data = f75_sheet_instance.batch_get(['A1:B100'])
        f75_data = f75_data[0]
        f75_headers = f75_data.pop(0)
        f75_df = pd.DataFrame(f75_data, columns=f75_headers)
        f75_df['Total Distance (KM)'] = pd.to_numeric(f75_df['Total Distance (KM)'])
        f75_df = f75_df.sort_values(by="Total Distance (KM)", ascending=False)
        f75 = f75_df.values.tolist()
        rank = 0
        space = 0
        for index in range(len(f75)):
            if index == 0:
                rank += 1
                f75[index].insert(0, rank)
            else:
                if f75[index][1] != f75[index - 1][2]: 
                    rank += 1 + space
                    space = 0
                else:
                    space += 1
                f75[index].insert(0, rank)
        values = f75

    # Individual Female 100KM Leaderboard
    elif category == "f100_leaderboard":
        category = "Individual Female 100KM"
        indiv_sheet = client.open("Individual Leaderboards")
        indiv_sheet_list = indiv_sheet.worksheets()
        f100_sheet_instance = indiv_sheet_list[7]
        f100_data = f100_sheet_instance.batch_get(['A1:B100'])
        f100_data = f100_data[0]
        f100_headers = f100_data.pop(0)
        f100_df = pd.DataFrame(f100_data, columns=f100_headers)
        f100_df['Total Distance (KM)'] = pd.to_numeric(f100_df['Total Distance (KM)'])
        f100_df = f100_df.sort_values(by="Total Distance (KM)", ascending=False)
        f100 = f100_df.values.tolist()
        rank = 0
        space = 0
        for index in range(len(f100)):
            if index == 0:
                rank += 1
                f100[index].insert(0, rank)
            else:
                if f100[index][1] != f100[index - 1][2]: 
                    rank += 1 + space
                    space = 0
                else:
                    space += 1
                f100[index].insert(0, rank)
        values = f100

    # Team 42KM Leaderboard
    elif category == "t42_leaderboard":
        category = "Team 42KM"
        team_sheet = client.open("Team Leaderboards")
        team_sheet_list = team_sheet.worksheets()
        t42_sheet_instance = team_sheet_list[0]
        t42_data = t42_sheet_instance.batch_get(['A1:B100'])
        t42_data = t42_data[0]
        t42_headers = t42_data.pop(0)
        t42_df = pd.DataFrame(t42_data, columns=t42_headers)
        t42_df['Total Distance (KM)'] = pd.to_numeric(t42_df['Total Distance (KM)'])
        t42_df = t42_df.sort_values(by="Total Distance (KM)", ascending=False)
        t42 = t42_df.values.tolist()
        rank = 0
        space = 0
        for index in range(len(t42)):
            if index == 0:
                rank += 1
                t42[index].insert(0, rank)
            else:
                if t42[index][1] != t42[index - 1][2]: 
                    rank += 1 + space
                    space = 0
                else:
                    space += 1
                t42[index].insert(0, rank)
        values = t42

    # Team 200KM Leaderboard
    else:
        category = "Team 200KM"
        team_sheet = client.open("Team Leaderboards")
        team_sheet_list = team_sheet.worksheets()
        t200_sheet_instance = team_sheet_list[1]
        t200_data = t200_sheet_instance.batch_get(['A1:B100'])
        t200_data = t200_data[0]
        t200_headers = t200_data.pop(0)
        t200_df = pd.DataFrame(t200_data, columns=t200_headers)
        t200_df['Total Distance (KM)'] = pd.to_numeric(t200_df['Total Distance (KM)'])
        t200_df = t200_df.sort_values(by="Total Distance (KM)", ascending=False)
        t200 = t200_df.values.tolist()
        rank = 0
        space = 0
        for index in range(len(t200)):
            if index == 0:
                rank += 1
                t200[index].insert(0, rank)
            else:
                if t200[index][1] != t200[index - 1][2]: 
                    rank += 1 + space
                    space = 0
                else:
                    space += 1
                t200[index].insert(0, rank)
        values = t200

    return render_template("leaderboards.html", values=values, category=category)


@app.route("/partners")
def partners():
    # NTURO Partners Page
    return render_template("partners.html")


@app.route("/faq")
def faq():
    # NTURO FAQ Page
    return render_template("faq.html")


@app.route("/contact")
def contact():
    # NTURO Contact Page
    return render_template("contact.html")


@app.route("/indiv_registration", methods=["GET", "POST"])
def indiv_registration():
    # NTURO Individual Registration Page

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Store registration information into Excel

        # Get Gender & Race Category
        sheet_name = request.form.get("indiv_cat")
        gender = request.form.get("gender")
        race_cat = "Indiv"+sheet_name
        name = request.form.get("name")

        # Define Google Sheets Name
        if gender == "male":
            gsheet_name = "Individual Male Registration"
        else:
            gsheet_name = "Individual Female Registration"

        # Get Sheet Number based on Sheet Name
        if sheet_name == "10km":
            sheet_number = 0
        elif sheet_name == "42km":
            sheet_number = 1
        elif sheet_name == "75km":
            sheet_number = 2
        else:
            sheet_number = 3 

        # Get entire spreadsheet
        sheet = client.open(gsheet_name)
        # Get relevant sheet
        sheet_instance = sheet.get_worksheet(sheet_number)

        # Create row for new registration info
        new_reg_info = [name, gender, request.form.get("email"), request.form.get("dob"), request.form.get("phone"),
                        request.form.get("nric"), request.form.get("address"), request.form.get("shirt_size")] 

        # Update sheet
        sheet_instance.append_row(new_reg_info)

        # Redirect to PAYMENT PAGE        
        return redirect(url_for("payment", race_cat=race_cat, name=name, gender=gender))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Show registration form
        return render_template("indiv_registration.html")


@app.route("/bundle_indiv_registration", methods=["GET", "POST"])
def bundle_indiv_registration():
    # NTURO Bundle Individual Registration Page

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Store registration information into Excel

        # Get Race Category (same for all)
        sheet_name = request.form.get("indiv_cat")
        race_cat = "Bundled_Indiv"+sheet_name    

        # Get Names & Gender
        name1 = request.form.get("name1")
        name2 = request.form.get("name2")
        name3 = request.form.get("name3")
        name = name1 + "," + name2 + "," + name3 
        gender1 = request.form.get("gender1")
        gender2 = request.form.get("gender2")
        gender3 = request.form.get("gender3")
        gender = gender1 + "," + gender2 + "," + gender3   

        # Get Sheet Number based on Sheet Name
        if sheet_name == "75km":
            sheet_number = 2
        else:
            sheet_number = 3 

        # Define Google Sheets Names
        gsheet_name_male = "Individual Male Registration"
        gsheet_name_female = "Individual Female Registration"

        # Get entire spreadsheets
        if gender1 == "male":
            sheet = client.open(gsheet_name_male)
        else:
            sheet = client.open(gsheet_name_female)
        # Get relevant sheet
        sheet_instance = sheet.get_worksheet(sheet_number)

        # Create rows for new registration info
        new_reg_info1 = [name1, gender1, request.form.get("email1"), request.form.get("dob1"), request.form.get("phone1"),
                        request.form.get("nric1"), request.form.get("address1"), request.form.get("shirt_size1")] 
        new_reg_info2 = [name2, gender2, request.form.get("email2"), request.form.get("dob2"), request.form.get("phone2"),
                        request.form.get("nric2"), request.form.get("address2"), request.form.get("shirt_size2")] 
        new_reg_info3 = [name3, gender3, request.form.get("email3"), request.form.get("dob3"), request.form.get("phone3"),
                        request.form.get("nric3"), request.form.get("address3"), request.form.get("shirt_size3")] 

        # Update sheets with 1st Participant's Information
        sheet_instance.append_row(new_reg_info1)

        # Update sheets with 2nd Participant's Information
        if gender2 == gender1:
            sheet_instance.append_row(new_reg_info2)
        else:
            if gender2 == "male":
                sheet = client.open(gsheet_name_male)
            else:
                sheet = client.open(gsheet_name_female)
            # Get relevant sheet
            sheet_instance = sheet.get_worksheet(sheet_number)
            sheet_instance.append_row(new_reg_info2)

        # Update sheets with 3rd Participant's Information
        if gender3 == gender2:
            sheet_instance.append_row(new_reg_info3)
        else:
            if gender3 == "male":
                sheet = client.open(gsheet_name_male)
            else:
                sheet = client.open(gsheet_name_female)
            # Get relevant sheet
            sheet_instance = sheet.get_worksheet(sheet_number)
            sheet_instance.append_row(new_reg_info3)
        
        # Redirect to PAYMENT PAGE        
        return redirect(url_for("payment", race_cat=race_cat, name=name, gender=gender))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Show registration form
        return render_template("bundle_indiv_registration.html")


@app.route("/team_registration", methods=["GET", "POST"])
def team_registration():
    # NTURO Team Registration Page

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Store registration information into Excel

        # Get Race Category
        sheet_name = request.form.get("team_cat")
        race_cat = "Team" + sheet_name 
        name = request.form.get("name")
        gender = request.form.get("gender")

        # Define Google Sheets Name
        gsheet_name = "Team Registration" 
        
        # Get Sheet Number based on Sheet Name
        if sheet_name == "42km":
            sheet_number = 0
        else:
            sheet_number = 1

        # Get entire spreadsheet
        sheet = client.open(gsheet_name)
        # Get relevant sheet
        sheet_instance = sheet.get_worksheet(sheet_number)

        # Create row for new registration info
        new_reg_info = [name, gender, request.form.get("email"), request.form.get("dob"),
                        request.form.get("phone"), request.form.get("nric"), request.form.get("address"), request.form.get("team_name"),
                        request.form.get("members_names"), request.form.get("shirt_size")] 

        # Update sheet
        sheet_instance.append_row(new_reg_info)
        
        # Redirect to PAYMENT PAGE        
        return redirect(url_for('payment', race_cat=race_cat, name=name, gender=gender))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Show registration form
        return render_template("team_registration.html")


@app.route("/payment/<race_cat>/<name>/<gender>", methods=["GET", "POST"])
def payment(race_cat, name, gender):
    # NTURO Payment Page

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get uploaded payment screenshot
        payment_img = request.files.get("payment_screenshot") 

        # Send file to email
        msg_subject = race_cat + " Payment"
        msg = Message(msg_subject, recipients=["nturo.finance@gmail.com"])
        msg.body = "Payment made by {name} ({gender}) for {race_cat}".format(name=name.upper(), race_cat=race_cat, gender=gender.upper())
        if payment_img:
            msg.attach(payment_img.filename, "image/*",payment_img.read())
        mail.send(msg)

        # Redirect to SUCCESS PAGE
        return redirect("/success")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Render Payment Page (NEED TO UPDATE PRICES ACCORDINGLY)
        qr_code_path = "/static/images/paynow_qr_code/" + race_cat + ".jpeg"
        if race_cat == "Indiv10km":
            race_cat = "Individual 10KM"
            amount = "$12"
        elif race_cat == "Indiv42km":
            race_cat = "Individual 42KM"
            amount = "$15"
        elif race_cat== "Indiv75km":
            race_cat = "Individual 75KM"
            amount = "$20"
        elif race_cat == "Indiv100km":
            race_cat = "Individual 100KM"
            amount = "$25"
        elif race_cat == "Team42km":
            race_cat = "Team 42KM"
            amount = "$15"
        elif race_cat == "Team200km":
            race_cat = "Team 200KM"
            amount = "$20"
        elif race_cat == "Bundled_Indiv75km":
            race_cat = "Bundled Individual 75KM"
            amount = "$51"
        else:
            race_cat = "Bundled Individual 100KM"
            amount = "$66"
        return render_template("payment.html", qr_code_path=qr_code_path, race_cat=race_cat, amount=amount, name=name, gender=gender)


@app.route("/success")
def success():
    return render_template("success.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)