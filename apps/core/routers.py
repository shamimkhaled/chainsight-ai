import random


class ReadReplicaRouter:
    """
    Database router for read/write splitting
    """

    def db_for_read(self, model, **hints):
        """
        Reads go to a replica
        """
        replicas = ['replica_1', 'replica_2']
        return random.choice(replicas)

    def db_for_write(self, model, **hints):
        """
        Writes always go to primary
        """
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if all models are in the same database
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Only allow migrations on the primary database
        """
        return db == 'default'