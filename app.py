from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Session verilerini şifrelemek için güvenli bir anahtar (Hoca sorarsa: Session güvenliği için şart de)
app.secret_key = 'seng_final_project_secret_key'

DATABASE = 'database.db'

# Veritabanı bağlantısını sağlayan ve sorguları ham (raw) çalıştıran yardımcı fonksiyon
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Sözlük yapısında veri dönmesini sağlar
    return conn

# Veritabanını ve tabloları database.sql dosyasından okuyarak ilk kez oluşturan fonksiyon
def init_db():
    conn = get_db_connection()
    with open('database.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()

# --- AUTHENTICATION (KAYIT VE GİRİŞ SİSTEMİ) ---

# 1. REGISTER (Kullanıcı Kayıt) Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        
        if not username or not password:
            flash('Lütfen tüm alanları doldurun!', 'danger')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            # RAW SQL: Kullanıcıyı ekliyoruz [cite: 119, 120]
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Bu kullanıcı adı zaten alınmış!', 'danger')
        finally:
            conn.close()
            
    return render_template('register.html')

# 2. LOGIN (Kullanıcı Girişi) Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        
        conn = get_db_connection()
        # RAW SQL: Kullanıcıyı arıyoruz [cite: 119]
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            # Giriş başarılıysa session bilgilerini cookielere atıyoruz [cite: 113]
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Tekrar hoş geldin, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Hatalı kullanıcı adı veya şifre!', 'danger')
            
    return render_template('login.html')

# 3. LOGOUT (Çıkış Yapma) Route
@app.route('/logout')
def logout():
    session.clear() # Oturumu sonlandır [cite: 113]
    flash('Başarıyla çıkış yapıldı.', 'success')
    return redirect(url_for('login'))


# --- APPLICATION LOGIC & CRUD (KOLLEKSİYON YÖNETİMİ) ---

# 1. READ: Kullanıcı Paneli ve İpuçları/İstatistikler [US2]
@app.route('/')
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    
    # RAW SQL: Sadece bu kullanıcıya ait verileri listele (Multi-user koruması) [cite: 114, 119, 122]
    items = conn.execute('SELECT * FROM collections WHERE user_id = ? ORDER BY id DESC', (session['user_id'],)).fetchall()
    
    # İş Mantığı (Business Logic): İstatistikleri SQL ile çekiyoruz
    total_books = conn.execute('SELECT COUNT(*) FROM collections WHERE user_id = ? AND type = "Kitap"', (session['user_id'],)).fetchone()[0]
    total_movies = conn.execute('SELECT COUNT(*) FROM collections WHERE user_id = ? AND type = "Film"', (session['user_id'],)).fetchone()[0]
    avg_rating = conn.execute('SELECT AVG(rating) FROM collections WHERE user_id = ?', (session['user_id'],)).fetchone()[0]
    
    conn.close()
    
    stats = {
        'total_books': total_books,
        'total_movies': total_movies,
        'avg_rating': avg_rating
    }
    
    return render_template('dashboard.html', items=items, stats=stats)

# 2. CREATE: Koleksiyona Yeni Öge Ekleme [US1]
@app.route('/add_item', methods=['POST'])
def add_item():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    title = request.form['title'].strip()
    item_type = request.form['type']
    author_director = request.form['author_director'].strip()
    rating = int(request.form['rating'])
    status = request.form['status']
    
    if not title or not author_director:
        flash('Lütfen zorunlu alanları boş bırakmayın!', 'danger')
        return redirect(url_for('dashboard'))
        
    conn = get_db_connection()
    # RAW SQL kullanımı [cite: 119]
    conn.execute('''
        INSERT INTO collections (user_id, title, type, author_director, rating, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session['user_id'], title, item_type, author_director, rating, status))
    conn.commit()
    conn.close()
    
    flash(f'"{title}" başarıyla koleksiyonunuza eklendi! [US1]', 'success')
    return redirect(url_for('dashboard'))

# 3. DELETE: Koleksiyondan Öge Silme [US3]
@app.route('/delete_item/<int:item_id>')
def delete_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    # GÜVENLİK KONTROLÜ: Silinmek istenen öge gerçekten bu kullanıcıya mı ait? [cite: 114, 122]
    item = conn.execute('SELECT * FROM collections WHERE id = ? AND user_id = ?', (item_id, session['user_id'])).fetchone()
    
    if item:
        conn.execute('DELETE FROM collections WHERE id = ?', (item_id,))
        conn.commit()
        flash('Öge koleksiyondan kaldırıldı. [US3]', 'success')
    else:
        flash('Yetkisiz işlem veya öge bulunamadı!', 'danger')
        
    conn.close()
    return redirect(url_for('dashboard'))


# --- UYGULAMAYI BAŞLATAN ANA KAPILAR ---
if __name__ == '__main__':
    init_db()  # Veritabanı tablolarını yoksa otomatik açar [cite: 120]
    app.run(debug=True)