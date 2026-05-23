import unittest
from src.scorer import LeadScorer

class TestLeadScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = LeadScorer()

    def test_is_qualified_success(self):
        # Лид подходит: рейтинг 4.0, 50 отзывов, есть негатив без ответа
        place_data = {
            'name': 'Good Restaurant',
            'rating': 4.0,
            'user_ratings_total': 50,
            'reviews': [
                {'rating': 5, 'text': 'Great!'},
                {'rating': 2, 'text': 'Bad service', 'owner_response': None}
            ]
        }
        self.assertTrue(self.scorer.is_qualified(place_data))

    def test_is_qualified_low_reviews(self):
        # Лид не подходит: мало отзывов
        place_data = {
            'name': 'Small Cafe',
            'rating': 4.0,
            'user_ratings_total': 10,
            'reviews': [{'rating': 2, 'text': 'Bad'}]
        }
        self.assertFalse(self.scorer.is_qualified(place_data))

    def test_is_qualified_wrong_rating(self):
        # Лид не подходит: слишком высокий рейтинг
        place_data = {
            'name': 'Perfect Place',
            'rating': 4.9,
            'user_ratings_total': 100,
            'reviews': [{'rating': 2, 'text': 'Rare bad day'}]
        }
        self.assertFalse(self.scorer.is_qualified(place_data))

    def test_is_qualified_no_negative_without_reply(self):
        # Лид не подходит: на все негативные отзывы есть ответы
        place_data = {
            'name': 'Responsive Place',
            'rating': 4.0,
            'user_ratings_total': 50,
            'reviews': [
                {'rating': 2, 'text': 'Bad service', 'owner_response': 'Sorry about that'}
            ]
        }
        self.assertFalse(self.scorer.is_qualified(place_data))

if __name__ == '__main__':
    unittest.main()
