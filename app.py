import os
import re
import shutil

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import pandas as pd

from utils import PDF, ResumeRanker, ResumeChecker
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
    ner = [CustomNER().process_text(resume["text"]) for resume in resume_text][0]

    job_role = JobClassifier().predict_job_role(resume_text[0]["text"])

    links = " ".join(resume_text[0]["links"])
    stop_words = []
    for key in ner.keys():
        if key in ["skill", "org", "per", "loc", "education", "deg"]:
            stop_words.extend(ner[key])

    pattern = r"\b(?:" + "|".join(map(re.escape, stop_words)) + r")\b"
    resume_text[0]["text"] = re.sub(pattern, "", resume_text[0]["text"])

    resume_health = ResumeChecker().perform_all_checks(resume_text[0]["text"] + links)
    shutil.rmtree("uploads")
    return templates.TemplateResponse(
        request=request,
        name="job-seeker-report.html",
        context={"ner": ner, "job_role": job_role, "resume_health": resume_health},
    )


def calculate_ranking(pdf_reader, job_description):
    resume_texts = [resume for resume in pdf_reader if resume["status"]]
    error_files = [
        [resume["filename"], resume["text"]]
        for resume in pdf_reader
        if not resume["status"]
    ]
    ranking = ResumeRanker().get_similarity(job_description, resume_texts)
    return error_files, ranking


@app.post("/recruiter/match1")
async def resume_ranking_pdf(
    request: Request,
    job_description: str = Form(...),
    pdf_file: list[UploadFile] = File(...),
):
    os.mkdir("./uploads")
    filenames = []
    for file in pdf_file:
        with open(f"uploads/{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        filenames.append(f"./uploads/{file.filename}")

    pdf_reader = PDF(filenames).process_pdf(path_type="file")
    error_files, ranking = calculate_ranking(pdf_reader, job_description)

    shutil.rmtree("uploads")

    return templates.TemplateResponse(
        request=request,
        name="recruiter-match.html",
        context={"ranking": ranking, "error": error_files},
    )


@app.post("/recruiter/match2")
async def resume_ranking_excel(
    request: Request,
    job_description: str = Form(...),
    excel_file: UploadFile = File(...),
):
    if not excel_file:
        raise FileNotFoundError("Excel File not Uploaded")

    os.mkdir("./uploads")
    with open(f"uploads/{excel_file.filename}", "wb") as buffer:
        shutil.copyfileobj(excel_file.file, buffer)
        filename = f"./uploads/{excel_file.filename}"

    files = pd.read_excel(filename).iloc[:, 0].tolist()
    pdf_reader = PDF(files).process_pdf(path_type="url")
    error_files, ranking = calculate_ranking(pdf_reader, job_description)

    shutil.rmtree("uploads")

    return templates.TemplateResponse(
        request=request,
        name="recruiter-match.html",
        context={"ranking": ranking, "error": error_files},
    )


@app.post("/recruiter/match3")
async def resume_ranking_drive(
    request: Request,
    job_description: str = Form(...),
    google_link: UploadFile = File(...),
):
    if not google_link:
        raise ValueError("Links not submitted")
    else:
        google_link = google_link.split(",")
        pdf_reader = PDF(google_link).process_pdf(path_type="url")
    error_files, ranking = calculate_ranking(pdf_reader, job_description)

    return templates.TemplateResponse(
        request=request,
        name="recruiter-match.html",
        context={"ranking": ranking, "error": error_files},
    )
