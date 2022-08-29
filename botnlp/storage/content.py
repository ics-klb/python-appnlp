# -*- coding: utf-8 -*-
"""
A Botnlp storage adapter that returns information about the request.
"""
from botnlp.storage.adapter import StorageAdapter

class TextStoreAdapter(StorageAdapter):
    """
    This is an class that represents the interface
    that all storage adapters should implement.
    """

    def __init__(self, **kwargs):
        super(TextStoreAdapter, self).__init__(**kwargs)


    def get_statement_model(self):
        """
        Return the class for the statement model.
        """
        from botnlp.storage.contentchemy.models import Statement

        # Create a storage-aware statement
        statementmodel = Statement
        statementmodel.storage = self

        return statementmodel

    def get_tag_model(self):
        from botnlp.storage.contentchemy.models import Tag
        # Create a storage-aware statement
        tagmodel = Tag
        tagmodel.storage = self

        return tagmodel

    def get_to_object(self, statement_data):
        """
        Return Statement object when given data
        returned from Mongo DB.
        """
        Statement = self.get_model('statement')

        statement_data['id'] = statement_data['_id']

        return Statement(**statement_data)


    def count(self):
        return self.statements.count()


    def create(self, **kwargs):
        """
        Creates a new statement matching the keyword arguments specified.
        Returns the created statement.
        """
        Statement = self.get_model('statement')

        print('create 1:', Statement, kwargs)
        if 'tags' in kwargs:
            kwargs['tags'] = list(set(kwargs['tags']))

        if 'search_text' not in kwargs:
            kwargs['search_text'] = self.tagger.get_text_index_string(kwargs['text'])

        if 'search_in_response_to' not in kwargs:
            if kwargs.get('in_response_to'):
                kwargs['search_in_response_to'] = self.tagger.get_text_index_string(kwargs['in_response_to'])

        inserted = self.statements.insert_one(kwargs)

        kwargs['id'] = inserted.inserted_id
        print('create 2:', kwargs)
        return Statement(**kwargs)


    def create_many(self, statements):
        """
        Creates multiple statement entries.
        """
        create_statements = []

        for statement in statements:
            statement_data = statement.serialize()
            tag_data = list(set(statement_data.pop('tags', [])))
            statement_data['tags'] = tag_data

            if not statement.search_text:
                statement_data['search_text'] = self.tagger.get_text_index_string(statement.text)

            if not statement.search_in_response_to and statement.in_response_to:
                statement_data['search_in_response_to'] = self.tagger.get_text_index_string(statement.in_response_to)

            create_statements.append(statement_data)

        print(create_statements)
        raise self.StorageException(
            'Either a statement not object Model'
        )
        # self.statements.insert_many(create_statements)


    def update(self, statement):
        data = statement.serialize()
        data.pop('id', None)
        data.pop('tags', None)

        data['search_text'] = self.tagger.get_text_index_string(data['text'])

        if data.get('in_response_to'):
            data['search_in_response_to'] = self.tagger.get_text_index_string(data['in_response_to'])

        update_data = {
            '$set': data
        }

        if statement.tags:
            update_data['$addToSet'] = {
                'tags': {
                    '$each': statement.tags
                }
            }

        search_parameters = {}

        if statement.id is not None:
            search_parameters['_id'] = statement.id
        else:
            search_parameters['text'] = statement.text
            search_parameters['conversation'] = statement.conversation

        update_operation = self.statements.update_one(
            search_parameters,
            update_data,
            upsert=True
        )

        if update_operation.acknowledged:
            statement.id = update_operation.upserted_id

        return statement

    def get_random(self):
        """
        Returns a random statement from the database
        """
        from random import randint

        count = self.count()

        if count < 1:
            raise self.EmptyDatabaseException()

        random_integer = randint(0, count - 1)

        statements = self.statements.find().limit(1).skip(random_integer)

        return self.get_to_object(list(statements)[0])

    def remove(self, statement_text):
        """
        Removes the statement that matches the input text.
        """
        self.statements.delete_one({'text': statement_text})

    def drop(self):
        """
        Remove the database.
        """
        self.client.drop_database(self.database.name)
