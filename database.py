import json
import os
import shutil

from git import Repo


class Database:
    def __init__(self, username, password, repo):
        self.database_storage = f'./{username}-database'
        shutil.rmtree(self.database_storage, ignore_errors=True)
        remote = f"https://{username}:{password}@{repo}"
        Repo.clone_from(remote, self.database_storage, branch='main')
        self.repo = Repo(self.database_storage)

    def find_all(self, table):
        table_file = f'{self.database_storage}/{table}.json'
        if os.path.exists(table_file):
            with open(table_file, 'r') as outfile:
                return json.load(outfile)
        else:
            return []

    def save(self, table, item):
        table_file = f'{self.database_storage}/{table}.json'
        if os.path.exists(table_file):
            with open(table_file, 'r') as outfile:
                data = json.load(outfile)
                data.append(item)
            with open(table_file, 'w') as outfile:
                json.dump(data, outfile, indent=2)
        else:
            with open(table_file, 'w') as outfile:
                json.dump([item], outfile, indent=2)
        self.repo.git.add(f'{table}.json')
        self.repo.index.commit(f'update {table}')
        self.repo.remote(name="origin").push()
