import openai
import os
import csv

openai.api_key = os.environ["OPENAI_API_KEY"]

sysrole = "You're a pro chef teaching beginners"
prompt = "I want to cook steak"
suffix = "  For the instructions you output, output a csv format where each step of the recipe is a row with Recipe Name, Step Name, Step Description, a prerequisite step ( if any ), a subsequent step ( if any ), and Duration ( lower bound in minutes ) and Duration ( upper bound in minutes ) such that 5-10 minutes would be 5 under Duration ( lower bound in minutes ) and 10 under Duration ( upper bound in minutes )"


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