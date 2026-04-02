import json
from flask import Flask, render_template, request, redirect, url_for
from database import execute_query

app = Flask(__name__)



@app.route("/")
def dashboard():
    company_count     = execute_query("SELECT COUNT(*) AS total FROM companies",    fetchone=True)
    job_count         = execute_query("SELECT COUNT(*) AS total FROM jobs",         fetchone=True)
    application_count = execute_query("SELECT COUNT(*) AS total FROM applications", fetchone=True)
    contact_count     = execute_query("SELECT COUNT(*) AS total FROM contacts",     fetchone=True)
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
            """INSERT INTO companies (company_name, industry, website, city, state, notes)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                request.form.get("company_name", "").strip(),
                request.form.get("industry", "").strip() or None,
                request.form.get("website", "").strip() or None,
                request.form.get("city", "").strip() or None,
                request.form.get("state", "").strip() or None,
                request.form.get("notes", "").strip() or None,
            ),
            commit=True
        )
        return redirect(url_for("companies"))
    return render_template("company_form.html", company=None)


@app.route("/companies/edit/<int:company_id>", methods=["GET", "POST"])
def edit_company(company_id):
    if request.method == "POST":
        execute_query(
            """UPDATE companies
               SET company_name=%s, industry=%s, website=%s, city=%s, state=%s, notes=%s
               WHERE company_id=%s""",
            (
                request.form.get("company_name", "").strip(),
                request.form.get("industry", "").strip() or None,
                request.form.get("website", "").strip() or None,
                request.form.get("city", "").strip() or None,
                request.form.get("state", "").strip() or None,
                request.form.get("notes", "").strip() or None,
                company_id,
            ),
            commit=True
        )
        return redirect(url_for("companies"))
    company = execute_query("SELECT * FROM companies WHERE company_id=%s", (company_id,), fetchone=True)
    return render_template("company_form.html", company=company)


@app.route("/companies/delete/<int:company_id>", methods=["POST"])
def delete_company(company_id):
    execute_query("DELETE FROM companies WHERE company_id=%s", (company_id,), commit=True)
    return redirect(url_for("companies"))



@app.route("/jobs")
def jobs():
    job_list = execute_query(
        """SELECT jobs.*, companies.company_name
           FROM jobs
           LEFT JOIN companies ON jobs.company_id = companies.company_id
           ORDER BY jobs.job_id DESC""",
        fetchall=True
    )
    # Deserialise requirements so templates get a plain list
    for job in job_list:
        job["requirements"] = _parse_requirements(job.get("requirements"))
    return render_template("jobs.html", jobs=job_list)


@app.route("/jobs/add", methods=["GET", "POST"])
def add_job():
    company_list = execute_query(
        "SELECT company_id, company_name FROM companies ORDER BY company_name",
        fetchall=True
    )
    if request.method == "POST":
        reqs_text = request.form.get("requirements", "")
        requirements_json = json.dumps(
            [s.strip() for s in reqs_text.split(",") if s.strip()]
        )
        execute_query(
            """INSERT INTO jobs
               (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                request.form.get("company_id") or None,
                request.form.get("job_title", "").strip(),
                request.form.get("job_type", "Full-time"),
                request.form.get("salary_min") or None,
                request.form.get("salary_max") or None,
                request.form.get("job_url", "").strip() or None,
                request.form.get("date_posted") or None,
                requirements_json,
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
        reqs_text = request.form.get("requirements", "")
        requirements_json = json.dumps(
            [s.strip() for s in reqs_text.split(",") if s.strip()]
        )
        execute_query(
            """UPDATE jobs
               SET company_id=%s, job_title=%s, job_type=%s, salary_min=%s, salary_max=%s,
                   job_url=%s, date_posted=%s, requirements=%s
               WHERE job_id=%s""",
            (
                request.form.get("company_id") or None,
                request.form.get("job_title", "").strip(),
                request.form.get("job_type", "Full-time"),
                request.form.get("salary_min") or None,
                request.form.get("salary_max") or None,
                request.form.get("job_url", "").strip() or None,
                request.form.get("date_posted") or None,
                requirements_json,
                job_id,
            ),
            commit=True
        )
        return redirect(url_for("jobs"))
    job = execute_query("SELECT * FROM jobs WHERE job_id=%s", (job_id,), fetchone=True)
    requirements_text = ", ".join(_parse_requirements(job.get("requirements"))) if job else ""
    return render_template("job_form.html", job=job, companies=company_list, requirements_text=requirements_text)


@app.route("/jobs/delete/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    execute_query("DELETE FROM jobs WHERE job_id=%s", (job_id,), commit=True)
    return redirect(url_for("jobs"))



@app.route("/applications")
def applications():
    application_list = execute_query(
        """SELECT applications.*, jobs.job_title, companies.company_name
           FROM applications
           LEFT JOIN jobs ON applications.job_id = jobs.job_id
           LEFT JOIN companies ON jobs.company_id = companies.company_id
           ORDER BY applications.application_date DESC""",
        fetchall=True
    )
    return render_template("applications.html", applications=application_list)


@app.route("/applications/add", methods=["GET", "POST"])
def add_application():
    job_list = execute_query(
        """SELECT jobs.job_id, jobs.job_title, companies.company_name
           FROM jobs
           LEFT JOIN companies ON jobs.company_id = companies.company_id
           ORDER BY jobs.job_title""",
        fetchall=True
    )
    if request.method == "POST":
        interview_data_text = request.form.get("interview_data", "").strip()
        if interview_data_text:
            try:
                interview_data_json = json.dumps(json.loads(interview_data_text))
            except json.JSONDecodeError:
                interview_data_json = json.dumps({"notes": interview_data_text})
        else:
            interview_data_json = None

        execute_query(
            """INSERT INTO applications
               (job_id, application_date, status, resume_version, cover_letter_sent, interview_data)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                request.form.get("job_id"),
                request.form.get("application_date"),
                request.form.get("status", "Applied"),
                request.form.get("resume_version", "").strip() or None,
                int(request.form.get("cover_letter_sent", 0)),
                interview_data_json,
            ),
            commit=True
        )
        return redirect(url_for("applications"))
    return render_template("application_form.html", application=None, jobs=job_list, interview_data_text="")


@app.route("/applications/edit/<int:application_id>", methods=["GET", "POST"])
def edit_application(application_id):
    job_list = execute_query(
        """SELECT jobs.job_id, jobs.job_title, companies.company_name
           FROM jobs
           LEFT JOIN companies ON jobs.company_id = companies.company_id
           ORDER BY jobs.job_title""",
        fetchall=True
    )
    if request.method == "POST":
        interview_data_text = request.form.get("interview_data", "").strip()
        if interview_data_text:
            try:
                interview_data_json = json.dumps(json.loads(interview_data_text))
            except json.JSONDecodeError:
                interview_data_json = json.dumps({"notes": interview_data_text})
        else:
            interview_data_json = None

        execute_query(
            """UPDATE applications
               SET job_id=%s, application_date=%s, status=%s, resume_version=%s,
                   cover_letter_sent=%s, interview_data=%s
               WHERE application_id=%s""",
            (
                request.form.get("job_id"),
                request.form.get("application_date"),
                request.form.get("status", "Applied"),
                request.form.get("resume_version", "").strip() or None,
                int(request.form.get("cover_letter_sent", 0)),
                interview_data_json,
                application_id,
            ),
            commit=True
        )
        return redirect(url_for("applications"))

    application = execute_query(
        "SELECT * FROM applications WHERE application_id=%s", (application_id,), fetchone=True
    )
    interview_data_text = ""
    if application and application["interview_data"]:
        val = application["interview_data"]
        interview_data_text = val if isinstance(val, str) else json.dumps(val, indent=2)
    return render_template("application_form.html", application=application, jobs=job_list,
                           interview_data_text=interview_data_text)


@app.route("/applications/delete/<int:application_id>", methods=["POST"])
def delete_application(application_id):
    execute_query("DELETE FROM applications WHERE application_id=%s", (application_id,), commit=True)
    return redirect(url_for("applications"))



@app.route("/contacts")
def contacts():
    contact_list = execute_query(
        """SELECT contacts.*, companies.company_name
           FROM contacts
           LEFT JOIN companies ON contacts.company_id = companies.company_id
           ORDER BY contacts.contact_name""",
        fetchall=True
    )
    return render_template("contacts.html", contacts=contact_list)


@app.route("/contacts/add", methods=["GET", "POST"])
def add_contact():
    company_list = execute_query(
        "SELECT company_id, company_name FROM companies ORDER BY company_name", fetchall=True
    )
    if request.method == "POST":
        execute_query(
            """INSERT INTO contacts
               (company_id, contact_name, title, email, phone, linkedin_url, notes)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                request.form.get("company_id") or None,
                request.form.get("contact_name", "").strip(),
                request.form.get("title", "").strip() or None,
                request.form.get("email", "").strip() or None,
                request.form.get("phone", "").strip() or None,
                request.form.get("linkedin_url", "").strip() or None,
                request.form.get("notes", "").strip() or None,
            ),
            commit=True
        )
        return redirect(url_for("contacts"))
    return render_template("contact_form.html", contact=None, companies=company_list)


@app.route("/contacts/edit/<int:contact_id>", methods=["GET", "POST"])
def edit_contact(contact_id):
    company_list = execute_query(
        "SELECT company_id, company_name FROM companies ORDER BY company_name", fetchall=True
    )
    if request.method == "POST":
        execute_query(
            """UPDATE contacts
               SET company_id=%s, contact_name=%s, title=%s, email=%s,
                   phone=%s, linkedin_url=%s, notes=%s
               WHERE contact_id=%s""",
            (
                request.form.get("company_id") or None,
                request.form.get("contact_name", "").strip(),
                request.form.get("title", "").strip() or None,
                request.form.get("email", "").strip() or None,
                request.form.get("phone", "").strip() or None,
                request.form.get("linkedin_url", "").strip() or None,
                request.form.get("notes", "").strip() or None,
                contact_id,
            ),
            commit=True
        )
        return redirect(url_for("contacts"))
    contact = execute_query("SELECT * FROM contacts WHERE contact_id=%s", (contact_id,), fetchone=True)
    return render_template("contact_form.html", contact=contact, companies=company_list)


@app.route("/contacts/delete/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):
    execute_query("DELETE FROM contacts WHERE contact_id=%s", (contact_id,), commit=True)
    return redirect(url_for("contacts"))



@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    matches = None          # None = page hasn't been submitted yet
    skills_input = ""

    if request.method == "POST":
        skills_input = request.form.get("skills", "")
        user_skills = {s.strip().lower() for s in skills_input.split(",") if s.strip()}

        if user_skills:
            job_list = execute_query(
                """SELECT jobs.job_id, jobs.job_title, jobs.requirements, companies.company_name
                   FROM jobs
                   LEFT JOIN companies ON jobs.company_id = companies.company_id""",
                fetchall=True
            )
            matches = []
            for job in job_list:
                job_reqs = _parse_requirements(job.get("requirements"))
                job_skills = {s.strip().lower() for s in job_reqs if s.strip()}

                matched = sorted(s for s in job_reqs if s.strip().lower() in user_skills)
                missing = sorted(s for s in job_reqs if s.strip().lower() not in user_skills)

                # Percentage based on how many of the JOB'S required skills the user has
                if job_skills:
                    pct = round(len([s for s in job_skills if s in user_skills]) / len(job_skills) * 100)
                else:
                    pct = 0

                matches.append({
                    "job_title":       job["job_title"],
                    "company_name":    job["company_name"] or "Unknown",
                    "match_percentage": pct,
                    "matched_skills":  matched,
                    "missing_skills":  missing,
                })
            matches.sort(key=lambda x: x["match_percentage"], reverse=True)
        else:
            matches = []

    return render_template("job_match.html", matches=matches, skills_input=skills_input)



def _parse_requirements(value):
    """Always return a plain Python list from a JSON string, list, or None."""
    if not value:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except (json.JSONDecodeError, ValueError):
            return []
    return []


if __name__ == "__main__":
    app.run(debug=True)