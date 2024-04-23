from flask import Flask, render_template, request
from jinja2 import Environment, FileSystemLoader

from utils import PDF, GitHubStatistics
from models import CustomNER, ResumeRanker, ResumeChecker, JobClassifier

import os

app = Flask(__name__)
env = Environment(loader=FileSystemLoader('.'))  # Load Jinja2 environment


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/jobseeker', methods=['POST'])
def jobseeker():
    return render_template('job-seeker-home.html')


@app.route('/jobseeker/upload', methods=['POST'])
def resume_report():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            ner, resume_health, job_role = {}, {}, {}
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            render_template('job-seeker-report.html')
            pdf_reader = PDF([filename])
            resume_text = [resume for resume in pdf_reader.process_pdf() if resume["status"]]

            ner = [CustomNER().process_text(resume["text"]) for resume in resume_text]
            ner = {key.lower(): [k.title() for k, v in ner[0].items() if v == key] for key in set(ner[0].values())}
            print(ner)
            job_role = JobClassifier().predict_job_role(resume_text[0]["text"])

            resume_text[0]["text"] = ''.join(resume_text[0]["text"].replace(skill, "") for skill in ner['skill'])
            links = " ".join(resume_text[0]["links"])
            resume_health = ResumeChecker().perform_all_checks(resume_text[0]["text"] + links)
    return render_template('job-seeker-report.html', values=dict({'ner':ner, 'resume_health': resume_health, 'job_role': job_role}))


@app.route('/recruiter', methods=['POST'])
def recruiter():
    return render_template('recruiter-home.html')


if __name__ == '__main__':
    app.run(debug=True)
