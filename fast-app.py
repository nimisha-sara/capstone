import shutil
from fastapi import FastAPI, UploadFile, File, Query

from utils import PDF, GitHubStatistics
from models import CustomNER, ResumeRanker, ResumeChecker, JobClassifier


app = FastAPI(
    title='Resume Analysis Tool'
)


@app.get("/")
def home():
    return {"Routes": ["/ranking", "/jobclassify", "/github", "/resumehealth"]}


@app.post('/ranking')
async def upload_file(
    job_description: str = Query(
        ...,
        description="Job Description of the role",
        example="We are seeking a skilled and motivated Software Engineer with a strong background in computer science, particularly in blockchain technology. As a Software Engineer, you will play a key role in designing, developing, and implementing blockchain-based solutions to address complex business challenges. You will collaborate with cross-functional teams to deliver high-quality software products that meet the needs of our clients and stakeholders."),
    uploaded_files: list[UploadFile] = File(..., description="Resume Files to Rank")
    ):
    pdf_reader = PDF([f"./tests/test_set/{file.filename}" for file in uploaded_files])
    resume_texts = [resume for resume in pdf_reader.process_pdf() if resume["status"]]

    ranking = ResumeRanker().get_similarity(
        job_description, 
        [resume["text"] for resume in resume_texts]
    )
    ner = [CustomNER().process_text(resume["text"]) for resume in resume_texts]

    return [{"match": ranking[i + 1], "NER": ner[i], "hyperlink": resume_texts[i]["links"]} for i in range(len(resume_texts))]


@app.post('/github')
async def github_analytics(username: str = Query(..., description="Github Username")):
    statistics = GitHubStatistics(username).get_statistics()
    if statistics:
        return statistics
    raise Exception("Github account NOT Found")


@app.post('/resumehealth')
async def resume_health(
    resume_text: str = Query(
        ...,
        description="Resume text to Check",
        example="EDUCATION Vellore Institute of Technology Vellore India Bachelor of Technology B.Tech Aug 2020 - June 2024  Major: Computer Science with specialization in Blockchain Technology  Achievement: Recognised as an Achiever 2021-2022 Clubs: IEEE-VIT ADG-VIT  Relevant Coursework: Predictive Analysis Statistics Data Structures & Algorithms Machine Learning ML WORK EXPERIENCE Razorpay Bangalore India Application Development Intern May 2023 - July 2023  Implemented robust monitoring and visualization strategies utilizing CloudWatch and Grafana catalyzing substantial improvements in resource allocation and system performance. ")
    ):
    checker = ResumeChecker().perform_all_checks(resume_text)
    return checker


@app.post('/jobclassify')
async def job_classify(
    file: UploadFile = File(
        ...,
        description="Resume File to Check")
    ):
    pdf_reader = PDF([f"./tests/test_set/{file.filename}"])
    resume_texts = [resume for resume in pdf_reader.process_pdf() if resume["status"]]
    classifier = JobClassifier().predict_job_role(resume_texts[0]["text"])
    return classifier
