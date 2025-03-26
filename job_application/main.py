import csv
from openai import OpenAI
from dotenv import dotenv_values
from datetime  import datetime

job_applicants_database="job_applicants.csv"
job_positions_database="job_positions.csv"
config = dotenv_values(".env")

def chatModel(prompt_message):
  client = OpenAI(api_key=config["OPENAI_API_KEY"])
  response = client.responses.create(
    model="gpt-3.5-turbo",
    input=[
      {
        "role": "assistant", "content": "You are a job application reviewer",
        "role": "user", "content": prompt_message
      }
    ]
  )
  
  return response.output_text

def aiAgent(applicant_data, job_position_details):
  prompt_message = f"""
  Instruction:
  REQUIRED SKILLS AND QUALIFICATIONS:
  Descriptions: {job_position_details['description']}
  Qualifications: {job_position_details['qualifications']}

  -----------------------------------------------------------------------------
  Return ONLY: "Qualified" or "Not Qualified"—no explanations, no extra text.
  Evaluation Process:

      Check if the applied job position exists in the list of available jobs.

      Compare the required skills for the job with the applicant's provided skills ({applicant_data['skills']}).

      If the applicant has at least 50% of the required skills, return "Qualified".

      If the applicant has less than 50% of the required skills, return "Not Qualified".

  Input:

      Applicant's Skills: {applicant_data['skills']}
  Output (Strict Format):

      "Qualified" (if skills meet at least 50% of job requirements)

      "Not Qualified" (if skills meet less than 50% of job requirements)

  ⚠️ DO NOT return any explanations, reasoning, or additional text. Only output "Qualified" or "Not Qualified" exactly as required.

  Example Outputs:
  ✅ Qualified
  ✅ Not Qualified
  """

  return chatModel(prompt_message)


def selectJobPosition():
  jobs_collection = printAndReturnAvailableJobs()
  selected_job = ""
  while True:
    selected_job = input("I am applying for: ")

    if selected_job in jobs_collection:
      break

  return selected_job

def printAndReturnAvailableJobs():
  print("Select the jobs")
  jobs_collection = []
  with open(job_positions_database, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
      job_position = row.get('job_position')
      print(job_position)
      jobs_collection.append(job_position)
  
  return tuple(jobs_collection)

def getJobPositionDetails(job_position_name):
  with open(job_positions_database, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
      if(row.get('job_position') == job_position_name):
        return row
  return "No job available"

def storeApplicants(data):
  with open(job_applicants_database, mode='a', newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
      data["name"], data["email"], data["applied_job_position"], data["skills"], data["applied_at"], data["birthdate"], data["application_status"]
    ])

def applicationForm():
  today = datetime.now()
  applicant_data = {}
  print("##JOB APPLICATION###")

  applicant_data['name'] = input("Name: ")
  applicant_data['skills'] = input("Skills: ")
  applicant_data['birthdate'] = input("Birthdate: ")
  applicant_data['email'] = input("Email: ")
  applicant_data['applied_job_position'] = selectJobPosition()
  applicant_data['applied_at'] = today.strftime("%Y-%m-%d %I:%M %p")

  return applicant_data

def main():
  applicant_data = applicationForm()
  job_position_details = getJobPositionDetails(applicant_data['applied_job_position'])
  applicant_data['application_status'] = aiAgent(applicant_data, job_position_details)
  storeApplicants(applicant_data)

  print(applicant_data)

main()