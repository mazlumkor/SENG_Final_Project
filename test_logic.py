import unittest

# İş mantığı (Business Logic) test fonksiyonumuz
def calculate_mock_stats(items):
    """Uygulamamızdaki SQL hesaplama mantığının kod seviyesindeki simülasyonu"""
    total_books = sum(1 for item in items if item['type'] == 'Kitap')
    total_movies = sum(1 for item in items if item['type'] == 'Film')
    avg_rating = sum(item['rating'] for item in items) / len(items) if items else 0.0
    
    return {
        'total_books': total_books,
        'total_movies': total_movies,
        'avg_rating': round(avg_rating, 1)
    }

class TestCollectionBusinessLogic(unittest.TestCase):
    
    def test_stats_calculation(self):
        # Test için örnek bir veri havuzu oluşturuyoruz
        mock_data = [
            {'type': 'Kitap', 'rating': 5},
            {'type': 'Kitap', 'rating': 3},
            {'type': 'Film', 'rating': 4}
        ]
        
        # Fonksiyonu çalıştırıyoruz
        result = calculate_mock_stats(mock_data)
        
        # Sonuçların doğruluğunu kılavuza uygun şekilde check ediyoruz (Unit Test)
        self.assertEqual(result['total_books'], 2)
        self.assertEqual(result['total_movies'], 1)
        self.assertEqual(result['avg_rating'], 4.0)

if __name__ == '__main__':
    unittest.main()