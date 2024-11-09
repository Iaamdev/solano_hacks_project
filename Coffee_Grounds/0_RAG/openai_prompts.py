import openai
import os
import csv

openai.api_key = os.environ["OPENAI_API_KEY"]

sysrole = "You're a pro chef teaching beginners"
prompt = "I want to make pork, a side dish, and a drink."
suffix = "  For the instructions you output, output a csv format where each step of the recipe is a row with Recipe Name, Step Name, Step Description, a prerequisite step ( if any ), a subsequent step ( if any ), and Duration ( lower bound in minutes ) and Duration ( upper bound in minutes ) such that 5-10 minutes would be 5 under Duration ( lower bound in minutes ) and 10 under Duration ( upper bound in minutes ). Follow the example below. Have as many parallel steps as possible. Only output the csv file with nothing else attached."
example = """Recipe Name,Step Name,Step Description,Prerequisite Step,Subsequent Step,Duration ( lower bound in minutes ),Duration ( upper bound in minutes )
Simple Steak Preparation,Prepare Steak,"Take the steak out of the fridge and let it come to room temperature.",,Season Steak,30,45
Simple Steak Preparation,Season Steak,"Season both sides of the steak with salt and pepper.",Prepare Steak,Heat Pan,1,2
Simple Steak Preparation,Heat Pan,"Heat a cast-iron skillet over high heat until it's very hot.",Season Steak,Add Oil,5,10
Simple Steak Preparation,Add Oil,"Add a high-smoke point oil like vegetable oil to the hot pan.",Heat Pan,Add Steak,1,1
Simple Steak Preparation,Add Steak,"Carefully place the steak in the hot pan.",Add Oil,Sear First Side,0,1
Simple Steak Preparation,Sear First Side,"Let the steak sear undisturbed until it forms a golden-brown crust.",Add Steak,Flip Steak,2,4
Simple Steak Preparation,Flip Steak,"Flip the steak to the other side.",Sear First Side,Sear Second Side,0,1
Simple Steak Preparation,Sear Second Side,"Sear the second side until it forms a crust.",Flip Steak,Check Internal Temperature,2,4
Simple Steak Preparation,Check Internal Temperature,"Use a thermometer to check the steak's temperature: 125°F for rare, 135°F for medium-rare, 145°F for medium.",Sear Second Side,Remove from Pan,1,1
Simple Steak Preparation,Remove from Pan,"Take the steak out of the pan and let it rest on a plate.",Check Internal Temperature,Rest Steak,0,1
Simple Steak Preparation,Rest Steak,"Let the steak rest for 5-10 minutes to retain its juices.",Remove from Pan,Serve Steak,5,10
Simple Steak Preparation,Serve Steak,"Slice the steak again"""

response = openai.chat.completions.create(
    model="gpt-4o",  # confirm
    messages = [
        {"role": "system", "content": sysrole},
        {"role": "user", "content": prompt + suffix + example}
    ]
)

output = response.choices[0].message.content
# print(output)

data_entry = [[sysrole, prompt, output]]
with open('output.csv', 'a+', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data_entry)