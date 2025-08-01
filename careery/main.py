from flask_babel import Babel, _
from flask_babelex import Babel, _
from flask import Flask, render_template, request
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Use your Groq API key
api_key = "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"
print(f"API Key loaded: {'Yes' if api_key else 'No'}")

if not api_key:
    print("Warning: No Groq API key found!")
    
client = Groq(api_key=api_key)

app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
babel = Babel(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/submit', methods=['POST'])
def submit():
    q1 = request.form['q1']
    q2 = request.form['q2']
    q3 = request.form['q3']
    q4 = request.form['q4']
    q5 = request.form['q5']
    q6 = request.form['q6']
    q7 = request.form['q7']
    q8 = request.form['q8']

    prompt = f"""
    I'm a university student seeking career guidance. Here are my responses to key questions:

    1. When my team was late on a project, I decided to: {q1}
    2. When I face a complex issue, my first action is: {q2}
    3. In case of conflict in a team, I usually: {q3}
    4. My ideal work environment is: {q4}
    5. I prefer to communicate by: {q5}
    6. My main interests and subjects I find fascinating are: {q6}
    7. In team projects, I naturally take the role of: {q7}
    8. When handling stress and deadlines, I: {q8}

    Based on these comprehensive responses, please provide a detailed career recommendation that includes:

    *Career Assessment Summary:*
    A brief analysis of my personality and work style

    *Recommended Career Paths:*
    • List 3-4 specific career options that match my profile
    • Include brief explanations for each recommendation

    *Key Skills to Develop:*
    • List important skills I should focus on
    • Mention specific courses or certifications

    *Helpful Resources:*
    • Include 2-3 relevant websites or platforms for learning
    • Suggest professional organizations or communities to join

    Please format your response with clear headings, bullet points, and separate paragraphs. Make it comprehensive but easy to read.
    """

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        raw_result = response.choices[0].message.content
        
        # Split into lines and process each line
        lines = raw_result.split('\n')
        formatted_lines = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                formatted_lines.append('</p><p>')
                continue
                
            # Handle headers (lines with **)
            if line.startswith('') and line.endswith(''):
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                header_text = line.replace('', '')
                formatted_lines.append(f'</p><h3>{header_text}</h3><p>')
                continue
                
            # Handle bullet points
            if line.startswith('•') or line.startswith('-'):
                if not in_list:
                    formatted_lines.append('</p><ul>')
                    in_list = True
                bullet_text = line[1:].strip()
                formatted_lines.append(f'<li>{bullet_text}</li>')
                continue
                
            # Regular text
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
                formatted_lines.append(f'</p><p>{line}')
            else:
                formatted_lines.append(line)
        
        if in_list:
            formatted_lines.append('</ul>')
            
        # Join and clean up
        result = ' '.join(formatted_lines)
        result = result.replace('</p><p></p><h3>', '</p><h3>')
        result = result.replace('</p><p></p><ul>', '</p><ul>')
        result = f'<p>{result}</p>'
        
    except Exception as e:
        print(f"Groq API Error: {e}")
        result = f"<p>Sorry, there was an error processing your request: {str(e)}</p>"
    
    return render_template('result.html', recommendation=result)

app.run(host='0.0.0.0', port=81)