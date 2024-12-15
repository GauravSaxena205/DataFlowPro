import json
import requests
import os
import google.generativeai as genai

import re
import ast
import traceback

import black 

CONFIG_PATH= 'C:\\Users\\gaura\\OneDrive\\Documents\\DataFlowPro\\configs\\sourceConfig.json'
SNOWFLAKE_CONFIG_PATH='C:\\Users\\gaura\\OneDrive\\Documents\\DataFlowPro\\configs\\snowflakeConnConfig.json'
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

SRC_LZ_MODEL='C:\\Users\\gaura\\OneDrive\\Documents\\DataFlowPro\\src\\Models\\SRC__LZ\\'
LZ_COMMON_MODEL='C:\\Users\\gaura\\OneDrive\\Documents\\DataFlowPro\\src\\Models\\LZ__COMMON\\'
COMMON_PUB_MODEL='C:\\Users\\gaura\\OneDrive\\Documents\\DataFlowPro\\src\\Models\\COMMON__PUB\\'



def load_config(config_path): 
    with open(config_path, 'r') as config_file: 
        return json.load(config_file) 
        
def generate_code_snippet(source_type, source_config): 
    prompt = f"Generate a Python function to load data from a {source_type} source with the following configuration: {source_config}" 
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    if hasattr(response,'text'):
        response_text = response.text
        code_pattern = r'```(?:python)?\n(.*?)```'
        matches = re.findall(code_pattern,response_text,re.DOTALL)
        extracted_codes = [code.strip() for code in matches]
        #print(extracted_codes)

    else:
        print('ERROR')
    return extracted_codes

def is_valid_python(code):
    try:
        ast.parse(str(code))
        return True
    except SyntaxError:
        return False
    
def format_python_code(code_snippet):
    try:
        # Use Black to format the code
        formatted_code = black.format_str(
            code_snippet, 
            mode=black.FileMode(
                line_length=88,  # Default Black line length
                string_normalization=True
            )
        )
        return formatted_code
    except black.InvalidInput as e:
        print(f"Error formatting code: {e}")
        return code_snippet    
    
def create_model(code_snippet,source_name,source_type,model_type):
    file_path=SRC_LZ_MODEL+f'{source_type}__{source_name}.py'
    code_snippet = str(code_snippet).strip()
    special_characters = ['[', ']']
    for char in special_characters: 
        code_snippet = code_snippet.replace(char, '')
    if model_type == 'LZ': 
        try:
            
            # Format the code snippet using Black 
            formatted_code = format_python_code(code_snippet)

            with open(file_path, "w") as write_data: 
                write_data.write(formatted_code) 
                print(f"File created successfully: {file_path}") 
        except Exception as e: 
            print(f"An error occurred while writing the file: {e}")

    
def process_source(source_type,source_name, source_config): 
    code_snippet = generate_code_snippet(source_type, source_config) 
    #create_model(code_snippet,source_name,source_type,'LZ')

  
def main(config_path): 
    config = load_config(config_path) 
  
    try:
        for source_type, sources in config.items(): 
            for source_name, source_config in sources.items(): 
                process_source(source_type,source_name,source_config) 
                
    except Exception as e :
        error_message = traceback.format_exc()
        return False, "", error_message


            
if __name__ == "__main__": main(CONFIG_PATH)