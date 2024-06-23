#code_generator.py file that contains functions to generate React code based on a prompt and determine the most appropriate CodeSandbox environment based on the prompt. The generate_react_code function uses the Litellm completion function to generate React code based on the given prompt. The determine_sandbox_environment function uses the Litellm completion function to determine the most appropriate CodeSandbox environment based on the given prompt. The functions handle errors and return default values if necessary.

import os
from litellm import completion

def generate_react_code(prompt):
    try:
        response = completion(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a React expert. Generate clean, efficient, and modern React code based on the given prompt."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error generating code: {e}")
        return None

def determine_sandbox_environment(prompt):
    try:
        response = completion(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Determine the most appropriate CodeSandbox environment based on the given prompt. Options include: react, vanilla, vue, angular, svelte, preact, typescript, nextjs, nuxtjs, gatsby, node, python, fastapi, flask, django."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content'].strip().lower()
    except Exception as e:
        print(f"Error determining sandbox environment: {e}")
        return "react"  # Default to React if unable to determine