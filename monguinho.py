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

    def to_doc(self, field_name, short=False):
        if isinstance(self.value, MissingField):
            return {}
        if short:
            field_name = self.name
        return {field_name: self.value}


class Embed(object):
    def __init__(self, name, required=True, default=MissingField()):
        self.name = name
        self.required = required
        self.value = self
        self._fields = {}

    def from_mixed(self, mixed, short):
        for field_name, field_data in self._fields.items():
            if short:
                field_name = field_data.name
            try:
                if isinstance(field_data, Embed):
                    field_data._setupFields()
                    field_data.from_mixed(mixed[field_name], short)
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

    def to_doc(self, short=False):
        doc = {}
        for field_name, field_data in self._fields.items():
            if isinstance(field_data.value, MissingField):
                continue
            elif isinstance(field_data, Embed):
                if short:
                    field_name = field_data.name
                doc.update({field_name: field_data.to_doc(short)})
            else:
                doc.update(field_data.to_doc(field_name, short))
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
    def __init__(self, mixed={}, short=False):
        cls = type(self)
        for field_name, field_data in cls._fields.items():
            if short:
                field_name = field_data.name
            try:
                if isinstance(field_data, Embed):
                    field_data._setupFields()
                    field_data.from_mixed(mixed[field_name], short)
                else:
                    field_data.value = mixed[field_name]
            except KeyError:
                if field_data.required:
                    if isinstance(field_data.value, MissingField):
                        raise RequiredField('"{}" field is required'.format(field_name))
                else:
                    field_data.value = MissingField()

    def to_doc(self, short=False):
        cls = type(self)
        doc = {}
        for field_name, field_data in cls._fields.items():
            if isinstance(field_data.value, MissingField):
                continue
            elif isinstance(field_data, Embed):
                if short:
                    field_name = field_data.name
                doc.update({field_name: field_data.to_doc(short)})
            else:
                doc.update(field_data.to_doc(field_name, short))
        return doc
