import openai
import os
import csv

openai.api_key = os.environ["OPENAI_API_KEY"]

sysrole = "Engineer"
prompt = "Tell me what to do to learn git"


response = openai.chat.completions.create(
    model="gpt-4o",  # confirm
    messages = [
        {"role": "system", "content": sysrole},
        {"role": "user", "content": prompt}
    ]
)

output = response.choices[0].message.content
print(output)

data_entry = [[sysrole, prompt, output]]
with open('output.csv', 'a+', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data_entry)