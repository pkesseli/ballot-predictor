import aiosqlite
import os

from pathlib import Path
from typing import Coroutine, Iterable


SQLITE_DATABASE: str = "../resources/openthesaurus/openthesaurus.db"
"""str: Relative path from this module to the default SQLite database. This
database will be used in most production scenarios and is only configurable for
testing purposes."""


SQLITE_DUMP: str = "../resources/openthesaurus/openthesaurus_dump_ch_sqlite.sql"
"""str: OpenThesaurus SQLite dump originally downloaded from https://www.openthesaurus.de/about/download on 22/12/2023. Converted from MySQL to SQLite using the following steps:
1) Manually import into MySQL using [MySQL Workbench](https://dev.mysql.com/downloads/).
2) Export from MySQL into SQLite database using [mysql2sqlite](https://pypi.org/project/mysql-to-sqlite3/):
```bash
mysql2sqlite --mysql-database openthesaurus_ch --mysql-user <user> --sqlite-file src/python/bp/resources/openthesaurus/openthesaurus.db
```
3) Dump SQLite database to SQL file using the [SQLite CLI](https://www.sqlite.org/download.html):
```bash
sqlite3 src/python/bp/resources/openthesaurus/openthesaurus.db .dump >src/python/bp/resources/openthesaurus/openthesaurus_dump_ch_sqlite.sql
```
"""


class OpenThesaurus:
    """Helper class based on bundled resources in bp/resources/openthesaurus to
    access synonym and antonym information for terms.
    """

    def __init__(self, database: str = SQLITE_DATABASE):
        """Initialises and configures the SQLite connection without opening it.

        Args:
            database (str, optional): Path to SQLite database file to use. Will
            be creatd in __aenter__ if it does not exist. Defaults to
            SQLITE_DATABASE.
        """
        self.database = database

    async def __aenter__(self):
        """Opens the configured SQLite database connection."""
        module_location: str = os.path.dirname(__file__)
        path: str = os.path.join(module_location, self.database)
        should_initialise: bool = not os.path.isfile(path)

        self.connection = aiosqlite.connect(path)
        await self.connection.__aenter__()

        if should_initialise:
            script_path: str = os.path.join(module_location, SQLITE_DUMP)
            script: str = Path(script_path).read_text("utf8")
            await self.connection.executescript(script)
        return self

    async def find_synonyms(self, term: str) -> Coroutine[str, None, None]:
        """Finds all synonyms for term.

        Args:
            term (str): Term for which to find synonyms.

        Returns:
            List[str]: All found synonyms.
        """
        rows: Iterable[aiosqlite.Row] = await self.connection.execute_fetchall("""
            select
            	case when synonym.normalized_word is null
            		then synonym.word
            		else synonym.normalized_word
            	end as word
            from term as needle
            	inner join term as synonym
            		on synonym.synset_id = needle.synset_id
            where needle.word = ? and synonym.word != ?
        """, [term, term])
        return [row[0] for row in rows]

    async def find_antonyms(self, term: str) -> Coroutine[str, None, None]:
        """Finds all antonyms for term.

        Args:
            term (str): Term for which to find antonyms.

        Returns:
            List[str]: All found antonyms.
        """
        rows: Iterable[aiosqlite.Row] = await self.connection.execute_fetchall("""
            select
            	distinct
            	case when antonym.normalized_word is null
            		then antonym.word
            		else antonym.normalized_word
            	end as word
            from term_link
            	inner join term needle on term_link.term_id = needle.id
            	inner join term antonym on term_link.target_term_id  = antonym.id
            where term_link.link_type_id = 1
            	and needle.word = ?
        """, [term])
        return [row[0] for row in rows]

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> Coroutine:
        """Disposes the SQLite connection."""
        await self.connection.__aexit__(exc_type, exc_val, exc_tb)
