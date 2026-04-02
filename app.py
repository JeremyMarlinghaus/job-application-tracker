import json
from flask import Flask, render_template, request, redirect, url_for
from database import execute_query

app = Flask(__name__)


@app.route("/")
def dashboard():
    company_count = execute_query("SELECT COUNT(*) AS total FROM companies", fetchone=True)
    job_count = execute_query("SELECT COUNT(*) AS total FROM jobs", fetchone=True)
    application_count = execute_query("SELECT COUNT(*) AS total FROM applications", fetchone=True)
    contact_count = execute_query("SELECT COUNT(*) AS total FROM contacts", fetchone=True)

    application_statuses = execute_query(
        "SELECT status, COUNT(*) AS count FROM applications GROUP BY status ORDER BY count DESC",
        fetchall=True
    )

    return render_template(
        "dashboard.html",
        company_count=company_count["total"],
        job_count=job_count["total"],
        application_count=application_count["total"],
        contact_count=contact_count["total"],
        application_statuses=application_statuses
    )


@app.route("/companies")
def companies():
    company_list = execute_query("SELECT * FROM companies ORDER BY company_name", fetchall=True)
    return render_template("companies.html", companies=company_list)


@app.route("/companies/add", methods=["GET", "POST"])
def add_company():
    if request.method == "POST":
        execute_query(
            """
            INSERT INTO companies (company_name, industry, website, city, state, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                request.form["company_name"],
                request.form["industry"],
                request.form["website"],
                request.form["city"],
                request.form["state"],
                request.form["notes"]
            ),
            commit=True
        )
        return redirect(url_for("companies"))

    return render_template("company_form.html", company=None)


@app.route("/companies/edit/<int:company_id>", methods=["GET", "POST"])
def edit_company(company_id):
    if request.method == "POST":
        execute_query(
            """
            UPDATE companies
            SET company_name = %s,
                industry = %s,
                website = %s,
                city = %s,
                state = %s,
                notes = %s
            WHERE company_id = %s
            """,
            (
                request.form["company_name"],
                request.form["industry"],
                request.form["website"],
                request.form["city"],
                request.form["state"],
                request.form["notes"],
                company_id
            ),
            commit=True
        )
        return redirect(url_for("companies"))

    company = execute_query("SELECT * FROM companies WHERE company_id = %s", (company_id,), fetchone=True)
    return render_template("company_form.html", company=company)


@app.route("/companies/delete/<int:company_id>", methods=["POST"])
def delete_company(company_id):
    execute_query("DELETE FROM companies WHERE company_id = %s", (company_id,), commit=True)
    return redirect(url_for("companies"))


@app.route("/jobs")
def jobs():
    job_list = execute_query(
        """
        SELECT jobs.*, companies.company_name
        FROM jobs
        LEFT JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY jobs.job_id DESC
        """,
        fetchall=True
    )
    return render_template("jobs.html", jobs=job_list)


@app.route("/jobs/add", methods=["GET", "POST"])
def add_job():
    company_list = execute_query(
        "SELECT company_id, company_name FROM companies ORDER BY company_name",
        fetchall=True
    )

    if request.method == "POST":
        requirements_json = json.dumps(
            [skill.strip() for skill in request.form["requirements"].split(",") if skill.strip()]
        )

        execute_query(
            """
            INSERT INTO jobs (
                company_id, job_title, job_type, salary_min, salary_max,
                job_url, date_posted, requirements
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                request.form["company_id"] or None,
                request.form["job_title"],
                request.form["job_type"],
                request.form["salary_min"] or None,
                request.form["salary_max"] or None,
                request.form["job_url"],
                request.form["date_posted"] or None,
                requirements_json
            ),
            commit=True
        )
        return redirect(url_for("jobs"))

    return render_template("job_form.html", job=None, companies=company_list, requirements_text="")


@app.route("/jobs/edit/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):
    company_list = execute_query(
        "SELECT company_id, company_name FROM companies ORDER BY company_name",
        fetchall=True
    )

    if request.method == "POST":
        requirements_json = json.dumps(
            [skill.strip() for skill in request.form["requirements"].split(",") if skill.strip()]
        )

        execute_query(
            """
            UPDATE jobs
            SET company_id = %s,
                job_title = %s,
                job_type = %s,
                salary_min = %s,
                salary_max = %s,
                job_url = %s,
                date_posted = %s,
                requirements = %s
            WHERE job_id = %s
            """,
            (
                request.form["company_id"] or None,
                request.form["job_title"],
                request.form["job_type"],
                request.form["salary_min"] or None,
                request.form["salary_max"] or None,
                request.form["job_url"],
                request.form["date_posted"] or None,
                requirements_json,
                job_id
            ),
            commit=True
        )
        return redirect(url_for("jobs"))

    job = execute_query("SELECT * FROM jobs WHERE job_id = %s", (job_id,), fetchone=True)

    requirements_text = ""
    if job and job["requirements"]:
        requirements_value = job["requirements"]
        if isinstance(requirements_value, str):
            requirements_text = ", ".join(json.loads(requirements_value))
        else:
            requirements_text = ", ".join(requirements_value)

    return render_template(
        "job_form.html",
        job=job,
        companies=company_list,
        requirements_text=requirements_text
    )


@app.route("/jobs/delete/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    execute_query("DELETE FROM jobs WHERE job_id = %s", (job_id,), commit=True)
    return redirect(url_for("jobs"))


@app.route("/applications")
def applications():
    application_list = execute_query(
        """
        SELECT applications.*, jobs.job_title, companies.company_name
        FROM applications
        LEFT JOIN jobs ON applications.job_id = jobs.job_id
        LEFT JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY applications.application_date DESC
        """,
        fetchall=True
    )
    return render_template("applications.html", applications=application_list)


@app.route("/applications/add", methods=["GET", "POST"])
def add_application():
    job_list = execute_query(
        """
        SELECT jobs.job_id, jobs.job_title, companies.company_name
        FROM jobs
        LEFT JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY jobs.job_title
        """,
        fetchall=True
    )

    if request.method == "POST":
        interview_data_text = request.form["interview_data"].strip()

        if interview_data_text:
            try:
                interview_data_json = json.dumps(json.loads(interview_data_text))
            except json.JSONDecodeError:
                interview_data_json = json.dumps({"notes": interview_data_text})
        else:
            interview_data_json = None

        execute_query(
            """
            INSERT INTO applications (
                job_id, application_date, status, resume_version,
                cover_letter_sent, interview_data
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                request.form["job_id"],
                request.form["application_date"],
                request.form["status"],
                request.form["resume_version"],
                int(request.form["cover_letter_sent"]),
                interview_data_json
            ),
            commit=True
        )
        return redirect(url_for("applications"))

    return render_template(
        "application_form.html",
        application=None,
        jobs=job_list,
        interview_data_text=""
    )


@app.route("/applications/edit/<int:application_id>", methods=["GET", "POST"])
def edit_application(application_id):
    job_list = execute_query(
        """
        SELECT jobs.job_id, jobs.job_title, companies.company_name
        FROM jobs
        LEFT JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY jobs.job_title
        """,
        fetchall=True
    )

    if request.method == "POST":
        interview_data_text = request.form["interview_data"].strip()

        if interview_data_text:
            try:
                interview_data_json = json.dumps(json.loads(interview_data_text))
            except json.JSONDecodeError:
                interview_data_json = json.dumps({"notes": interview_data_text})
        else:
            interview_data_json = None

        execute_query(
            """
            UPDATE applications
            SET job_id = %s,
                application_date = %s,
                status = %s,
                resume_version = %s,
                cover_letter_sent = %s,
                interview_data = %s
            WHERE application_id = %s
            """,
            (
                request.form["job_id"],
                request.form["application_date"],
                request.form["status"],
                request.form["resume_version"],
                int(request.form["cover_letter_sent"]),
                interview_data_json,
                application_id
            ),
            commit=True
        )
        return redirect(url_for("applications"))

    application = execute_query(
        "SELECT * FROM applications WHERE application_id = %s",
        (application_id,),
        fetchone=True
    )

    interview_data_text = ""
    if application and application["interview_data"]:
        interview_value = application["interview_data"]
        if isinstance(interview_value, str):
            interview_data_text = interview_value
        else:
            interview_data_text = json.dumps(interview_value, indent=2)

    return render_template(
        "application_form.html",
        application=application,
        jobs=job_list,
        interview_data_text=interview_data_text
    )


@app.route("/applications/delete/<int:application_id>", methods=["POST"])
def delete_application(application_id):
    execute_query("DELETE FROM applications WHERE application_id = %s", (application_id,), commit=True)
    return redirect(url_for("applications"))


@app.route("/contacts")
def contacts():
    contact_list = execute_query(
        """
        SELECT contacts.*, companies.company_name
        FROM contacts
        LEFT JOIN companies ON contacts.company_id = companies.company_id
        ORDER BY contacts.contact_name
        """,
        fetchall=True
    )
    return render_template("contacts.html", contacts=contact_list)


@app.route("/contacts/add", methods=["GET", "POST"])
def add_contact():
    company_list = execute_query(
        "SELECT company_id, company_name FROM companies ORDER BY company_name",
        fetchall=True
    )

    if request.method == "POST":
        execute_query(
            """
            INSERT INTO contacts (
                company_id, contact_name, title, email,
                phone, linkedin_url, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                request.form["company_id"] or None,
                request.form["contact_name"],
                request.form["title"],
                request.form["email"],
                request.form["phone"],
                request.form["linkedin_url"],
                request.form["notes"]
            ),
            commit=True
        )
        return redirect(url_for("contacts"))

    return render_template("contact_form.html", contact=None, companies=company_list)


@app.route("/contacts/edit/<int:contact_id>", methods=["GET", "POST"])
def edit_contact(contact_id):
    company_list = execute_query(
        "SELECT company_id, company_name FROM companies ORDER BY company_name",
        fetchall=True
    )

    if request.method == "POST":
        execute_query(
            """
            UPDATE contacts
            SET company_id = %s,
                contact_name = %s,
                title = %s,
                email = %s,
                phone = %s,
                linkedin_url = %s,
                notes = %s
            WHERE contact_id = %s
            """,
            (
                request.form["company_id"] or None,
                request.form["contact_name"],
                request.form["title"],
                request.form["email"],
                request.form["phone"],
                request.form["linkedin_url"],
                request.form["notes"],
                contact_id
            ),
            commit=True
        )
        return redirect(url_for("contacts"))

    contact = execute_query("SELECT * FROM contacts WHERE contact_id = %s", (contact_id,), fetchone=True)
    return render_template("contact_form.html", contact=contact, companies=company_list)


@app.route("/contacts/delete/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):
    execute_query("DELETE FROM contacts WHERE contact_id = %s", (contact_id,), commit=True)
    return redirect(url_for("contacts"))


@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    matches = []

    if request.method == "POST":
        user_skills = {
            skill.strip().lower()
            for skill in request.form["skills"].split(",")
            if skill.strip()
        }

        job_list = execute_query(
            """
            SELECT jobs.job_title, jobs.requirements, companies.company_name
            FROM jobs
            LEFT JOIN companies ON jobs.company_id = companies.company_id
            """,
            fetchall=True
        )

        for job in job_list:
            requirements = []
            if job["requirements"]:
                requirements_value = job["requirements"]
                if isinstance(requirements_value, str):
                    requirements = json.loads(requirements_value)
                else:
                    requirements = requirements_value

            job_skills = {skill.strip().lower() for skill in requirements if skill.strip()}
            matched_skills = sorted(list(user_skills.intersection(job_skills)))
            missing_skills = sorted(list(job_skills.difference(user_skills)))
            match_percentage = round((len(matched_skills) / len(user_skills)) * 100) if user_skills else 0

            matches.append(
                {
                    "job_title": job["job_title"],
                    "company_name": job["company_name"],
                    "match_percentage": match_percentage,
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills
                }
            )

        matches.sort(key=lambda item: item["match_percentage"], reverse=True)

    return render_template("job_match.html", matches=matches)


if __name__ == "__main__":
    app.run(debug=True)
