from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="1234"
)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        technology = request.form['technology']
        correct_option = request.form['correct_option']

        # Insert the new question into the database
        cur = conn.cursor()
        cur.execute("INSERT INTO questions (question, option1, option2, option3, option4, technology, correct_option) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (question, option1, option2, option3, option4, technology, correct_option))
        conn.commit()
        cur.close()

        return redirect('/admin')

    # Retrieve all questions from the database
    cur = conn.cursor()
    cur.execute("SELECT * FROM questions")
    questions = cur.fetchall()
    cur.close()

    return render_template('admin.html', questions=questions)


@app.route('/admin/delete/<int:id>', methods=['POST'])
def delete_question(id):
    # Delete the question from the database
    cur = conn.cursor()
    cur.execute("DELETE FROM questions WHERE id = %s", (id,))
    conn.commit()
    cur.close()

    return redirect('/admin')


@app.route('/admin/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        # Delete all existing questions
        cur = conn.cursor()
        cur.execute("DELETE FROM questions")
        conn.commit()
        cur.close()

        # Delete all existing quiz questions
        cur = conn.cursor()
        cur.execute("DELETE FROM quiz")
        conn.commit()
        cur.close()

        # Add selected questions to the quiz
        selected_questions = request.form.getlist('selected_questions')
        for question_id in selected_questions:
            cur = conn.cursor()
            cur.execute("INSERT INTO quiz (question_id) VALUES (%s)", (question_id,))
            conn.commit()
            cur.close()

        return redirect('/admin')

    # Retrieve all questions from the database
    cur = conn.cursor()
    cur.execute("SELECT * FROM questions")
    questions = cur.fetchall()
    cur.close()

    return render_template('create_quiz.html', questions=questions)


@app.route('/admin/view_quiz')
def view_quiz():
    # Retrieve all questions from the quiz
    cur = conn.cursor()
    cur.execute("SELECT q.id, q.question, q.option1, q.option2, q.option3, q.option4, q.correct_option "
                "FROM quiz AS q INNER JOIN questions AS qs ON q.question_id = qs.id")
    quiz_questions = cur.fetchall()
    cur.close()

    return render_template('view_quiz.html', questions=quiz_questions)


@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        return redirect('/user/submit')

    # Retrieve all questions from the quiz
    cur = conn.cursor()
    cur.execute("SELECT q.id, q.question, q.option1, q.option2, q.option3, q.option4 "
                "FROM quiz AS q INNER JOIN questions AS qs ON q.question_id = qs.id")
    quiz_questions = cur.fetchall()
    cur.close()

    return render_template('user.html', questions=quiz_questions)


@app.route('/user/submit', methods=['POST'])
def submit_quiz():
    answers = request.form
    score = 0

    # Retrieve all questions from the quiz
    cur = conn.cursor()
    cur.execute("SELECT q.id, q.question, q.option1, q.option2, q.option3, q.option4, q.correct_option "
                "FROM quiz AS q INNER JOIN questions AS qs ON q.question_id = qs.id")
    quiz_questions = cur.fetchall()
    cur.close()

    # Calculate the score
    for question in quiz_questions:
        question_id = str(question[0])
        user_answer = answers.get(question_id)
        correct_answer = question[6]

        if user_answer == correct_answer:
            score += 1

    return render_template('result.html', score=score)


if __name__ == '__main__':
    app.run()
