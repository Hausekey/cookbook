import os
import tika
tika.initVM()
from tika import parser


def find_start_keyword(lines_list):
    placing = 0
    for line in lines_list:
        for keyword in keyword_start_synonyms:
            if line.find(keyword) > -1:
                return placing
        placing += 1
    return -1


def find_stop_keyword(lines_list):
    placing = 0
    for line in lines_list:
        for keyword in keyword_stop_synonyms:
            if line.find(keyword) > -1:
                return placing
        placing += 1
    return -1


keyword_start_synonyms = ['食材', '材料']
keyword_stop_synonyms = ['做法', '製作方式']
ingredient_str = ""

print(os.getcwd())
for filename in os.listdir(os.getcwd() + r'\recipes'):
    parsed = parser.from_file(r"C:\Users\Jackie\PycharmProjects\parsepdf\recipes" + '\\' + filename)
    recipe = parsed["content"]
    recipe_lines = recipe.split('\n')
    recipe_lines = list(filter(None, recipe_lines))
    print(recipe_lines)
    start_index = find_start_keyword(recipe_lines)
    stop_index = find_stop_keyword(recipe_lines)
    print(start_index)
    print(stop_index)

# for i in range(start_index, stop_index):
    





