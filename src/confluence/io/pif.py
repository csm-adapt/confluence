import pandas as pd
from pypif import pif
#
# # ##### B. Kappes additions
# import re
# from collections import OrderedDict
# from functools import partial
#
# # Convert from a pandas.DataFrame (df) to a pif.System (record)
# # Need: map from df.columns to record.{name, properties, preparation_steps, references, etc.}
# # For Quality Made:
# #   Sample Name --> record.name
# #   url_friendly(Sample Name) --> record.uid
# #   Parent Sample Name --> System.name --> record.subsystem.name
# #   url_friendly(Parent Sample Name) --> System.uid --> record.subsystem.uid
# #   FILE: description --> description --> record.property.name
# #   FILE: description --> each entry --> pif.FileReference --> record.property.file_reference
# #   All others: description (units) --> description, units
# #     pif.Property.name = description
# #     pif.Property.scalars.value = record entry (strip quotation marks)
# #     pif.Property.scalars.units = units
#
# class SchemaMap(OrderedDict):
#     """
#     Dictionary-like where stored keys are assumed to be regular expressions.
#     """
#     def __init__(self, *args, **kwds):
#         super().__init__(*args, **kwds)
#
#     def __getitem__(self, key):
#         for k,f in self._keymap:
#             if re.match(k, key):
#                 return partial(f, key)
#         raise KeyError(f"{key} not found.")
#
#
# class RecordHandler:
#     def __init__(self):
#         self._result = None
#         self._schema_map = SchemaMap()
#
#     def create(self):
#         raise NotImplementedError("Derived classes must implement 'create'.")
#
#     def populate(self, **kwds):
#         raise NotImplementedError("Derived classes must implement 'populate'.")
#
#     def finalize(self):
#         pass
#
#
# class QualityMadeToPIF(RecordHandler):
#     def __init__(self):
#         super().__init__()
#         # order is important!
#         self._schema_map['Sample Name'] = self._create_system_name_and_uid
#         self._schema_map['Parent Sample Name'] = self._create_system_name_and_uid
#         self._schema_map['FILE:'] = self._create_file_reference
#         self._schema_map['.*'] = self._create_property
#
#     @staticmethod
#     def _create_system_name_and_uid(key, value):
#         # create a pif.System
#         # set name
#         # set uid
#         pass
#
#     @staticmethod
#     def _create_file_reference(key, files):
#         # create a pif.Property
#         # set name (from SchemaMap key, which we don't have access to...
#         #   Use partial functions to have SchemaMap call function with key and value
#         #   This is what is currently implemented, but may be bad. :)
#         pass
#
#     @staticmethod
#     def _create_property(key, value):
#         # create pif.Property
#         # set name from key
#         # set units from key
#         # set scalar.value from value
#         pass
#
#
#     def create(self):
#         pass
#
#     def populate(self, **kwds):
#         for k,v in kwds.items():
#             self._schema_map(k, v)
#
# # #####




# ##### A. Mikulich additions
import re
from collections import OrderedDict
from functools import partial

# Convert from a pandas.DataFrame (df) to a pif.System (record)
# Need: map from df.columns to record.{name, properties, preparation_steps, references, etc.}
# For Quality Made:
#   Sample Name --> record.name
#   url_friendly(Sample Name) --> record.uid
#   Parent Sample Name --> System.name --> record.subsystem.name
#   url_friendly(Parent Sample Name) --> System.uid --> record.subsystem.uid
#   FILE: description --> description --> record.property.name
#   FILE: description --> each entry --> pif.FileReference --> record.property.file_reference
#   All others: description (units) --> description, units
#     pif.Property.name = description
#     pif.Property.scalars.value = record entry (strip quotation marks)
#     pif.Property.scalars.units = units


class SchemaMap(OrderedDict):
    """
    Dictionary-like where stored keys are assumed to be regular expressions.
    """
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self._keymap = OrderedDict()

    def __getitem__(self, key):
        for k,f in self._keymap.items():
            if re.match(k, key):
                return partial(f, key)
        raise KeyError(f"{key} not found.")

    def __setitem__(self, key, value):
        self._keymap[key] = value


class RecordHandler:
    def __init__(self):
        self._result = None
        self._schema_map = SchemaMap()

    def create(self):
        raise NotImplementedError("Derived classes must implement 'create'.")

    def populate(self, **kwds):
        raise NotImplementedError("Derived classes must implement 'populate'.")

    def finalize(self):
        pass


class QualityMadeToPIF(RecordHandler):
    def __init__(self):
        super().__init__()
        # order is important!
        self._schema_map['Sample Name'] = self._create_system_name_and_uid
        self._schema_map['Parent Sample Name'] = self._create_system_name_and_uid
        self._schema_map['FILE:'] = self._create_file_reference
        self._schema_map['.*'] = self._create_property

    @staticmethod
    def _create_system_name_and_uid(record, key, value):
        # create a pif.System
        # set name
        # set uid
        uid = value
        name = value
        record.uid = re.sub(r'\W', '', uid)
        record.names = name
        return record

    @staticmethod
    def _new_property(record, name):
        """
        Creates a new property named 'name' and puts it in `record`.

        :param record: pif.System object to which the property is to be added.
        :type record: pif.System.
        :param name: Name of the property
        :type name: str

        :returns: Reference to the newly created property.
        :rtype: pif.Property
        """
        dst = pif.Property(name=name)
        if record.properties:
            record.properties.append(dst)
        else:
            record.properties = [dst]
        return dst

    @staticmethod
    def _create_file_reference(key, value, record):
        # create a pif.Property
        # set name (from SchemaMap key, which we don't have access to...
        #   Use partial functions to have SchemaMap call function with key and value
        #   This is what is currently implemented, but may be bad. :)
        # Steps:
        # 1. strip FILE: from the key --> key
        key = key.strip("FILE: ").strip()
        # 2. split value into list [str(s).strip() for s in value.strip('"').strip('[]').split(',')] --> filenames
        filenames = [str(s).strip() for s in value.strip('"').strip('[]').split(',')]
        # 3. create property <- pif.Property(name=key)
        dst = QualityMadeToPIF._new_property(record, key)
        # 4. iterate through filenames --> property.reference = [pif.Reference(FILENAME=fname) for fname in filenames]
        dst.reference = [pif.Reference(relative_path=fname) for fname in filenames]
        # Double check relative path
        return record


    @staticmethod
    def _canonicalize_scalar(value):
        """Returns the value in its most natural representation."""
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return str(value)

    @staticmethod
    def _find_name_and_units(k):
        REunits = re.search(r'\([^)]+\)')
        k = k.strip()
        for match in re.findall(REunits, k):
            if k.endswith(match):
                first = k.strip(match).strip()
                last = match.strip('()').strip()
                return (first, last)
        return (k, None)



    @staticmethod
    def _create_property(record, key, value):
        # create pif.Property
        # 1. set name from key
        # 2. set units from key
        # name, units = re.search(r'([^(]+)\(?([^)]*)\)?').groups()
        name, units = QualityMadeToPIF._find_name_and_units(key)
        # 3. set scalar.value from value
        scalarvalue = pif.Scalar()
        scalarvalue.value = QualityMadeToPIF._canonicalize_scalar(value)
        record.properties.append(pif.Property(name=name, units=units, scalars=scalarvalue.value))
        return record

    def create(self):
        self._record = pif.System()


    def populate(self, **kwds):
        self.create()
        for k, v in kwds.items():
            self._record = self._schema_map[k](k, v, self._record)
        return self._record

# #####


# # ######
# # Branden's nonsensical returncode
#
# class BaseData(pd.DataFrame):
#     pass
#
# class PIFData(BaseData):
#     def schema_map(self, key):
#         # relies on self._schema_map defined, mapping strings to
#         pass
#
# class QMPIFData(PIFData):
#     def __init__(self, *args, **kwds):
#         super().__init__(*args, **kwds)
#         self._schema_map = {
#             'system.name': lambda s: re.match('Sample Name', s),
#             'reference': lambda s: re.match('^FILE:', s)
#         }
#
#     def dump(self, filestream):
#         # for each record:
#         # create pif.System() object
#         # name from Sample Name
#         # subsystem from Parent Sample Name
#         # FILE: --> reference object into "files" pif.Property(name="files")
#         #   Add each file as a pif.Reference() object
#         # All others are pif.Property with name = corresponding column names
#         #   and value = value from cell.
# # ######


class PifWriter():
    def __init__(self, fname=None, sheetname='Sheet1', **kwds):
        self._filename = None
        self.set_filename(fname)
        self._converter = QualityMadeToPIF()

    def set_filename(self, fname):
        self._filename = fname

    def get_filename(self):
        return self._filename

    def convert(self, df):
        """
        Converts a specialized CSV/TSV file to a physical information file.

        :param files: list of files to convert
        :return: yields PIFs created from the input files
        """
        keys = df.columns
        for index, values in df.iterrows():
            row = dict(zip(keys, values))
            record = self._converter.populate(**row)
            yield record


    def write(self, df, sheetname='Sheet1'):
        result = self.convert(df)
        with open(self.get_filename(), 'w+') as output_file:
            pif.dump(list(result), output_file, indent=2)
