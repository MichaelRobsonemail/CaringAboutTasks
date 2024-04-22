from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import datetime

app = Flask(__name__)
app.secret_key = 'secret'

users = {
    'user1': {'password': '1234', 'role': 'taskgiver', 'clicked': False, 'show_accept_bring_coffee_button': False},
    'user2': {'password': '1234', 'role': 'taskaceptar', 'clicked': False, 'accepted': False, 'taskgiver': None, 'eta': None, 'tasks': []}
}

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard', username=session['username']))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if username in users and users[username]['password'] == password and users[username]['role'] == role:
            session['username'] = username
            return redirect(url_for('dashboard', username=username))
        else:
            return render_template('login.html', error='Invalid username, password, or role')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard/<username>')
def dashboard(username):
    if 'username' in session and session['username'] == username:
        if username.startswith('user1'):
            return render_template('dashboard_user1.html', user1=users['user1'], user2=users['user2'])
        elif username.startswith('user2'):
            return render_template('dashboard_user2.html', user1=users['user1'], user2=users['user2'])
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route('/initiate_task', methods=['POST'])
def initiate_task():
    if 'username' in session:
        username = session['username']

        if username.startswith('user2'):
            task_name = request.form['task_name']
            users[username]['tasks'].append({'name': task_name, 'status': 'pending'})

            # Notify user1 about the task
            show_accept_bring_coffee_button()

            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Not authorized to initiate task'})
    else:
        return jsonify({'success': False, 'message': 'Not authenticated'})

@app.route('/accept_task', methods=['POST'])
def accept_task():
    if 'username' in session:
        username = session['username']

        if username.startswith('user1'):
            task_name = request.form['task_name']
            eta = request.form['eta']
            for task in users['user2']['tasks']:
                if task['name'] == task_name and task['status'] == 'pending':
                    task['status'] = 'accepted'
                    task['taskgiver'] = username
                    task['eta'] = eta

                    return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'message': 'Task not found or already accepted'})
        else:
            return jsonify({'success': False, 'message': 'Not authorized to accept task'})
    else:
        return jsonify({'success': False, 'message': 'Not authenticated'})

def show_accept_bring_coffee_button():
    users['user1']['show_accept_bring_coffee_button'] = True

if __name__ == '__main__':
    app.run(debug=True)