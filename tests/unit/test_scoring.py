import datetime
import unittest

import mock

from utils import cases, patch_redis
import scoring
import storage


class TestScoringSuite(unittest.TestCase):

    @cases([
        # phone and added score
        (None, 0),
        ('not empty', 1.5),
    ])
    @cases([
        # email and added score
        (None, 0),
        ('not empty', 1.5),
    ])
    @cases([
        # birthday, gender and added score
        (None, None, 0),
        (datetime.date(2020, 10, 2), None, 0),
        (None, 'not empty', 0),
        (datetime.date(2020, 10, 2), 'not empty', 1.5),
    ])
    @cases([
        # first_name, last_name and added score
        (None, None, 0),
        ('not empty', None, 0),
        (None, 'not empty', 0),
        ('not empty', 'not empty', 0.5),
    ])
    def test_get_score(self,
                       phone, phone_added_score,
                       email, email_added_score,
                       birthday, gender, birthday_gender_added_score,
                       first_name, last_name, name_added_score):

        expected_score = (
            phone_added_score +
            email_added_score +
            birthday_gender_added_score +
            name_added_score
        )
        mock_r = mock.Mock()
        mock_r.get.return_value = None
        mock_r.set.return_value = None
        with patch_redis(mock_r):
            actual_score = scoring.get_score(storage.Storage(),
                                             phone=phone,
                                             email=email,
                                             birthday=birthday,
                                             gender=gender,
                                             first_name=first_name,
                                             last_name=last_name)

        self.assertEqual(actual_score, expected_score)
