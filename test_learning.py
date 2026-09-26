import json
import unittest
from pathlib import Path
import core
import learning
from content import BY_ID, LESSONS, TOPICS


class LessonTests(unittest.TestCase):
    def test_export_and_unique_ids(self):
        exported = json.loads(Path(__file__).with_name("short_lessons.json").read_text(encoding="utf-8"))
        self.assertEqual(exported["lessons"], LESSONS)
        self.assertEqual(len(BY_ID), 60)
        self.assertEqual(len(TOPICS), 15)
        self.assertEqual(len({x["english"] for x in LESSONS}), 60)

    def test_cloze_and_pronunciation(self):
        for item in LESSONS:
            with self.subTest(lesson=item["id"]):
                self.assertIn(item["phrase"], item["english"])
                self.assertEqual(item["cloze"].replace("＿＿＿＿", item["phrase"], 1), item["english"])
                words = core.expected_phones(item["english"])
                self.assertTrue(words)
                self.assertTrue(all(phones for _, phones in words))
                card, text, answer, exercise = learning.lesson_parts(item["id"])
                self.assertNotIn(text, card)
                self.assertIn(text, answer)
                self.assertEqual(exercise, item["cloze"])

    def test_navigation_stays_in_topic_and_wraps(self):
        for topic in TOPICS:
            ids = [value for _, value in learning.lesson_choices(topic)]
            self.assertEqual(len(ids), 4)
            self.assertTrue(all(BY_ID[value]["topic"] == topic for value in ids))
            self.assertEqual(learning.next_lesson(topic, ids[-1]), ids[0])
            self.assertEqual(learning.next_lesson(topic, "old-id"), ids[0])


if __name__ == "__main__":
    unittest.main()
