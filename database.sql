-- 1. Tablo: Kullanıcı bilgileri (Kayıt ve Giriş için)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- 2. Tablo: Koleksiyon öğeleri (Kitap ve Filmler)
CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    type TEXT NOT NULL, -- 'Kitap' veya 'Film'
    author_director TEXT NOT NULL,
    rating INTEGER NOT NULL, -- 1 ile 5 arası puan
    status TEXT NOT NULL, -- 'Okundu', 'İzlendi', 'Planlanıyor'
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
