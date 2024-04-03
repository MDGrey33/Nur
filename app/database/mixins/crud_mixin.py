from app.database.database import get_db


class CRUDMixin:
    def get_or_create(self):
        db = get_db()
        filter_attrs = self.get_filter_attributes()
        filters = {attr: getattr(self, attr) for attr in filter_attrs}
        db_instance = db.query(type(self)).filter_by(**filters).first()

        if db_instance:
            return db_instance
        else:
            db.add(self)
            db.commit()
            db.refresh(self)
            return self

    def get_filter_attributes(self):
        """
        This method should be overridden by child classes to return a list of attribute names
        used for filtering when performing get_or_create operation.
        We use the filtering to identify if the object should be fetched or created
        """
        raise NotImplementedError("'get_filter_attributes' method must be implemented in child classes.")