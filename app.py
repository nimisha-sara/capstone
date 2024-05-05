from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import re
import shutil
import pandas as pd
from typing import Optional

from utils import PDF, GitHubStatistics, ResumeRanker, ResumeChecker
from models import CustomNER, JobClassifier


app = FastAPI(title="Resume Analysis Tool")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")


@app.post("/jobseeker")
def jobseeker(request: Request):
    return templates.TemplateResponse(request=request, name="job-seeker-home.html")


@app.post("/recruiter")
def recruiter(request: Request):
    return templates.TemplateResponse(request=request, name="recruiter-home.html")


@app.post("/jobseeker/report")
async def resume_report(request: Request, file: UploadFile = File(...)):
    os.mkdir("uploads")
    with open(f"uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    filename = f"./uploads/{file.filename}"
    pdf_reader = PDF([f"{filename}"])

    resume_text = [resume for resume in pdf_reader.process_pdf() if resume["status"]]
    ner = [CustomNER().process_text(resume["text"]) for resume in resume_text]
    # ner = {
    #     key.lower(): [k.title() for k, v in ner[0].items() if v == key]
    #     for key in set(ner[0].values())
    # }

    job_role = JobClassifier().predict_job_role(resume_text[0]["text"])

    words_to_replace = ner["skill"] + ner["org"]
    words_to_replace = [re.escape(word) for word in words_to_replace]
    replace_pattern = re.compile(
        r"\b(?:" + "|".join(words_to_replace) + r")\b", flags=re.IGNORECASE
    )
    resume_text[0]["text"] = replace_pattern.sub("", resume_text[0]["text"])

    links = " ".join(resume_text[0]["links"])

    resume_health = ResumeChecker().perform_all_checks(resume_text[0]["text"] + links)
    shutil.rmtree("uploads")
    return templates.TemplateResponse(
        request=request,
        name="job-seeker-report.html",
        context={"ner": ner, "job_role": job_role, "resume_health": resume_health},
    )


@app.post("/recruiter/match")
async def resume_ranking(
    request: Request,
    job_description: str = Form(...),
    action: str = Form(...),
    pdf_file: list[UploadFile] = File(...),
    google_link: str = File(...),
    excel_file: UploadFile = File(...),
):
    print("\n\n========================================\n")
    print(action, job_description, pdf_file, google_link, excel_file)
    if action == "pdf_file":
        if not pdf_file:
            raise FileNotFoundError("PDF File not Uploaded")
        else:
            os.mkdir("./uploads")
            filenames = []
            for file in pdf_file:
                with open(f"uploads/{file.filename}", "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                filenames.append(f"./uploads/{file.filename}")

            pdf_reader = PDF(filenames).process_pdf(path_type="file")
    elif action == "excel_file":
        if not excel_file:
            raise FileNotFoundError("Excel File not Uploaded")

        os.mkdir("./uploads")
        with open(f"uploads/{excel_file.filename}", "wb") as buffer:
            shutil.copyfileobj(excel_file.file, buffer)
            filename = f"./uploads/{excel_file.filename}"

        files = pd.read_excel(filename).iloc[:, 0].tolist()
        pdf_reader = PDF(files).process_pdf(path_type="url")

    elif action == "google_link":
        if not google_link:
            raise ValueError("Links not submitted")
        else:
            google_link = google_link.split(",")
            pdf_reader = PDF(google_link).process_pdf(path_type="url")
    else:
        print(f"ERORRRRR: action is ==={action}===")

    resume_texts = [resume for resume in pdf_reader if resume["status"]]
    error_files = [
        [resume["filename"], resume["text"]] for resume in pdf_reader if not resume["status"]
    ]
    print(f"\n\n========================================\n{resume_texts}\t{error_files}\n========================================\n")
    ranking = ResumeRanker().get_similarity(job_description, resume_texts)

    if action == "pdf_file":
        shutil.rmtree("uploads")
    print(f"\n\n========================================\n{ranking}\n========================================\n")

    return templates.TemplateResponse(
        request=request,
        name="recruiter-match.html",
        context={"ranking": ranking, "error": error_files},
    )
