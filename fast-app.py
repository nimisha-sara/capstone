from fastapi import FastAPI, UploadFile, File, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import shutil

from utils import PDF, GitHubStatistics
from models import CustomNER, ResumeRanker, ResumeChecker, JobClassifier


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
    with open(f"uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    filename = f"./uploads/{file.filename}"
    pdf_reader = PDF([f"{filename}"])

    resume_text = [resume for resume in pdf_reader.process_pdf() if resume["status"]]
    ner = [CustomNER().process_text(resume["text"]) for resume in resume_text]
    ner = {
        key.lower(): [k.title() for k, v in ner[0].items() if v == key]
        for key in set(ner[0].values())
    }

    job_role = JobClassifier().predict_job_role(resume_text[0]["text"])

    resume_text[0]["text"] = "".join(
        resume_text[0]["text"].replace(skill, "") for skill in ner["skill"]
    )
    links = " ".join(resume_text[0]["links"])
    resume_health = ResumeChecker().perform_all_checks(resume_text[0]["text"] + links)

    os.remove(filename)
    return templates.TemplateResponse(
        request=request,
        name="job-seeker-report.html",
        context={"ner": ner, "job_role": job_role, "resume_health": resume_health},
    )


@app.post("/ranking")
def upload_file(
    job_description: str = Query(
        ...,
        description="Job Description of the role",
        examples="We are seeking a skilled and motivated Software Engineer with a strong background in computer science, particularly in blockchain technology. As a Software Engineer, you will play a key role in designing, developing, and implementing blockchain-based solutions to address complex business challenges. You will collaborate with cross-functional teams to deliver high-quality software products that meet the needs of our clients and stakeholders.", # type: ignore
    ),
    uploaded_files: list[UploadFile] = File(..., description="Resume Files to Rank"),
):
    pdf_reader = PDF([f"./tests/test_set/{file.filename}" for file in uploaded_files])
    resume_texts = [resume for resume in pdf_reader.process_pdf() if resume["status"]][
        0
    ]

    ranking = ResumeRanker().get_similarity(
        job_description, [resume["text"] for resume in resume_texts]
    )
    ner = [CustomNER().process_text(resume["text"]) for resume in resume_texts]

    return [
        {"match": ranking[i + 1], "NER": ner[i], "hyperlink": resume_texts[i]["links"]}
        for i in range(len(resume_texts))
    ]


@app.post("/resumehealth")
def resume_health(
    resume_text: str = Query(
        ...,
        description="Resume text to Check",
        examples="EDUCATION Vellore Institute of Technology Vellore India Bachelor of Technology B.Tech Aug 2020 - June 2024  Major: Computer Science with specialization in Blockchain Technology  Achievement: Recognised as an Achiever 2021-2022 Clubs: IEEE-VIT ADG-VIT  Relevant Coursework: Predictive Analysis Statistics Data Structures & Algorithms Machine Learning ML WORK EXPERIENCE Razorpay Bangalore India Application Development Intern May 2023 - July 2023  Implemented robust monitoring and visualization strategies utilizing CloudWatch and Grafana catalyzing substantial improvements in resource allocation and system performance. ", # type: ignore
    )
):
    checker = ResumeChecker().perform_all_checks(resume_text)
    return checker
