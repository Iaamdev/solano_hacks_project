import csv
import os

import openai
import pandas as pd

openai.api_key = os.environ["OPENAI_API_KEY"]
complete = False

BORDER = "_____________________________________"

while not complete:
    # sysrole = "Engineer"
    print(BORDER)
    prompt = input("What can I help you with?:\n").upper()
    if prompt == "EXIT":
        complete = True
    else:
        pass

    response = openai.chat.completions.create(
        model="gpt-4o",  # confirm
        messages=[
            # {"role": "system", "content": sysrole},
            {"role": "user", "content": prompt},
        ],
    )

    output = response.choices[0].message.content
    print(output)

    data_entry = [[prompt, output]]
    with open("output.csv", "a+", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data_entry)

    file_reader = pd.read_csv("output.csv")

    print(BORDER)

    is_complete = input("Are you finished? (Y or N):\n").upper()
    if is_complete == "Y":
        complete = True
    elif is_complete == "N":
        pass
