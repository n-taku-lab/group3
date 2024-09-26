from flask import Flask, render_template, request, redirect, jsonify
import mysql.connector


app = Flask(__name__, static_folder='./templates/images')

# MySQLデータベースへの接続
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='nttwest',
        password='hoge',
        database='mydb'
    )
    return connection

@app.route('/')
def index():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # buildingsテーブルから建物情報を取得
    cursor.execute('SELECT id, name, address FROM buildings')
    buildings = cursor.fetchall()
    # データベースからid=1の建物のnameを取得
    cursor.execute('SELECT name FROM buildings WHERE id = 1')
    name = cursor.fetchone()


    cursor.close()
    connection.close()

    return render_template('index.html', buildings=buildings, name=name)
    # return render_template('index.html', name=name)
    # return render_template('index.html')

@app.route('/update', methods=['POST'])
def update():
    new_value = request.form['new_value']
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # データベースの値を更新
    cursor.execute('UPDATE buildings SET name = %s WHERE id = 1', (new_value,))
    connection.commit()
    
    cursor.close()
    connection.close()
    
    return redirect('/')
# 建物の詳細ページを表示
@app.route('/building<int:building_id>')
def building_detail(building_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # 建物の紹介文と住所を取得
    cursor.execute('SELECT name, description, address FROM buildings WHERE id = %s', (building_id,))
    building = cursor.fetchone()
    # 口コミ情報を取得
    cursor.execute('SELECT id, review, is_reported FROM reviews WHERE building_id = %s', (building_id,))
    reviews = cursor.fetchall()

    cursor.close()
    connection.close()

    if building is None:
        return "建物が見つかりません", 404
    # return render_template('building1.html')
    return render_template('building'+str(building_id)+'.html', building=building, reviews=reviews)

# 口コミの追加 (Ajax経由で呼び出し)
@app.route('/add_review', methods=['POST'])
def add_review():
    review_text = request.form['review_text']
    
    connection = get_db_connection()
    cursor = connection.cursor()

    # 建物1に対して口コミを追加
    cursor.execute('INSERT INTO reviews (building_id, review) VALUES (%s, %s)', (1, review_text))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({'status': 'success'})

# 口コミを通報する処理
@app.route('/report_review', methods=['POST'])
def report_review():
    review_id = request.form['review_id']

    connection = get_db_connection()
    cursor = connection.cursor()

    # 口コミを通報としてマーク
    cursor.execute('UPDATE reviews SET is_reported = TRUE WHERE id = %s', (review_id,))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    app.run(debug=True)
