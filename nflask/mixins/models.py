import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.usertype import UserType
from nflask.models import Model
from nflask.utils import datettime_locale_now, datettime_locale_server
import datetime

tanggal = datettime_locale_now()


class BaseModel(Model):
    id = columns.UUID(
        primary_key=True,
        default=uuid.uuid1)

    __abstract__ = True

    # @classmethod
    def to_dict(self):
        prev = super(BaseModel, self).to_dict()
        # Add id field into serialized data
        prev.update(id=str(self.id))

        return prev


class CommonInfo(BaseModel):
    """
        Abstract models to implements DRY
        across all models
    """
    created_by_id = columns.UUID()
    created_by_email = columns.Text()
    created_by_nama = columns.Text()
    created_date = columns.DateTime(
        default=datettime_locale_now())
    updated_by_id = columns.UUID()
    updated_by_email = columns.Text()
    updated_date = columns.DateTime()
    is_deleted = columns.Boolean(
        index=True,
        default=False)
    deleted_by_id = columns.UUID()
    deleted_by_email = columns.Text()
    deleted_date = columns.DateTime()

    __abstract__ = True

    def update(self, **kwargs):
        if self.is_deleted:
            self.deleted_date = datettime_locale_now()
        else:
            self.updated_date = datettime_locale_now()

        return super(CommonInfo, self).update(**kwargs)

    def to_dict(self):
        prev = super(CommonInfo, self).to_dict()
        # Assign field
        updated_by_id = None
        updated_date = None
        if self.updated_by_id is not None:
            updated_by_id = str(self.updated_by_id)
        if self.updated_date is not None:
            updated_date = self.updated_date.strftime(
                "%Y-%m-%d %H:%M:%S")
        # Add fields into serialized data

        prev.update(
            created_by_id=str(self.created_by_id),
            created_by_email=self.created_by_email,
            created_by_nama=self.created_by_nama,
            created_date=self.created_date.strftime("%Y-%m-%d %H:%M:%S"),
            updated_by_id=updated_by_id,
            updated_by_email=self.updated_by_email,
            updated_date=updated_date
        )

        return prev

class PermissionType(UserType):
    """
        Define permissions
    """
    creates = columns.Boolean(default=False)
    reads = columns.Boolean(default=False)
    updates = columns.Boolean(default=False)
    deletes = columns.Boolean(default=False)
    imports = columns.Boolean(default=False)
    exports = columns.Boolean(default=False)
    prints = columns.Boolean(default=False)

    def to_dict(self):
        return {
            "creates": self.creates,
            "reads": self.reads,
            "updates": self.updates,
            "deletes": self.deletes,
            "imports": self.imports,
            "exports": self.exports,
            "prints": self.prints
        }
