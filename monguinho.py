#coding: utf-8

class RequiredField(Exception):
    pass

class MissingField(object):
    pass


class Field(object):
    def __init__(self, name, required=True, default=MissingField()):
        self.name = name
        self.required = required
        self.value = default

    def to_doc(self):
        if isinstance(self.value, MissingField):
            return {}
        return {self.name: self.value}


class Embed(object):
    def __init__(self, name, required=True):
        self.name = name
        self.required = required
        self.value = self
        self._fields = {}

    def from_mixed(self, mixed):
        for field_name, field_data in self._fields.items():
            try:
                if isinstance(field_data, Embed):
                    field_data._setupFields()
                    field_data.from_mixed(mixed[field_name])
                else:
                    field_data.value = mixed[field_name]
            except KeyError:
                if field_data.required:
                    if isinstance(field_data.value, MissingField):
                        raise RequiredField('"{}" field is required'.format(field_name))
                else:
                    field_data.value = MissingField()

    def _setupFields(self):
        for member_name, member_value in self.__dict__.items():
            if member_name in ['name', 'required', 'value',  '_fields']:
                continue
            self._fields[member_name] = member_value
        self.__initialized = True

    def to_doc(self):
        doc = {}
        for field_name, field_data in self._fields.items():
            if isinstance(field_data.value, MissingField):
                continue
            elif isinstance(field_data, Embed):
                doc.update({field_data.name: field_data.to_doc()})
            else:
                doc.update(field_data.to_doc())
        return doc


class DocumentMeta(type):
    def __new__(cls, name, parents, dct):
        fields = {}
        for member_name, member_value in dct.items():
            if callable(member_value) or member_name in ['__qualname__', '__module__']:
                continue
            fields[member_name] = member_value
        dct['_fields'] = fields
        return super(DocumentMeta, cls).__new__(cls, name, parents, dct)


class Document(object, metaclass=DocumentMeta):
    def __init__(self, mixed={}):
        cls = type(self)
        for field_name, field_data in cls._fields.items():
            try:
                if isinstance(field_data, Embed):
                    field_data._setupFields()
                    field_data.from_mixed(mixed[field_name])
                else:
                    field_data.value = mixed[field_name]
            except KeyError:
                if field_data.required:
                    if isinstance(field_data.value, MissingField):
                        raise RequiredField('"{}" field is required'.format(field_name))
                else:
                    field_data.value = MissingField()


    def to_doc(self):
        cls = type(self)
        doc = {}
        for field_name, field_data in cls._fields.items():
            if isinstance(field_data.value, MissingField):
                continue
            elif isinstance(field_data, Embed):
                doc.update({field_data.name: field_data.to_doc()})
            else:
                doc.update(field_data.to_doc())
        return doc