#!/usr/bin/env python3
"""
Simple test version of the Flask app to debug issues
"""

from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test App</title>
        <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    </head>
    <body>
        <h1>Test Registration</h1>
        <form id="testForm">
            <input type="text" id="name" placeholder="Name" required><br><br>
            <input type="email" id="email" placeholder="Email" required><br><br>
            <button type="submit">Test Submit</button>
        </form>
        
        <div id="result"></div>
        
        <script>
        $('#testForm').on('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                name: $('#name').val(),
                email: $('#email').val()
            };
            
            console.log('Sending data:', formData);
            
            $.ajax({
                url: '/test-register',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(formData),
                success: function(response) {
                    console.log('Success:', response);
                    $('#result').html('<p style="color: green;">Success: ' + response.message + '</p>');
                },
                error: function(xhr) {
                    console.log('Error:', xhr);
                    const response = xhr.responseJSON;
                    $('#result').html('<p style="color: red;">Error: ' + (response ? response.error : 'Unknown error') + '</p>');
                }
            });
        });
        </script>
    </body>
    </html>
    '''

@app.route('/test-register', methods=['POST'])
def test_register():
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
            
        name = data.get('name')
        email = data.get('email')
        
        if not name or not email:
            return jsonify({'error': 'Name and email required'}), 400
            
        return jsonify({'message': f'Registration successful for {name} ({email})'})
        
    except Exception as e:
        print(f"Error in test_register: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting test Flask app...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
