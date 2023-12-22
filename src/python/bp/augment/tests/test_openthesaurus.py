from bp.augment.openthesaurus import OpenThesaurus

import os
import tempfile
import unittest

from typing import List


class TestOpenthesaurus(unittest.IsolatedAsyncioTestCase):

    async def test_create_database_if_not_exists(self):
        database: str
        with tempfile.NamedTemporaryFile() as temp_file_generator:
            database = temp_file_generator.name

        try:
            async with OpenThesaurus(database):
                self.assertGreaterEqual(os.path.getsize(database), 50 << 20)
        finally:
            os.remove(database)

    async def test_find_synonyms(self):
        async with OpenThesaurus() as thesaurus:
            synonyms: List[str] = await thesaurus.find_synonyms("Junge")
            self.assertCountEqual(["Knirps", "Knabe", "Bub", "Wicht", "Bube", "Pimpf", "Steppke", "Kerlchen",
                                  "Jungchen", "Bengel", "Kleiner", "Kurzer", "Bauer", "Bube", "Unter", "Wuenscher"], synonyms)

    async def test_find_antonyms(self):
        async with OpenThesaurus() as thesaurus:
            antonyms: List[str] = await thesaurus.find_antonyms("Mann")
            self.assertCountEqual(["Frau"], antonyms)
